#include "FourLineFeedbackNetwork.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <string>

using soundlab::research::FourLineFeedbackNetwork;

namespace {
int failures = 0;

void expect(bool condition, const std::string& message) {
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << message << '\n';
    }
}

float energy(const FourLineFeedbackNetwork::LineValues& values) {
    float sum = 0.0F;
    for (const float value : values) {
        sum += value * value;
    }
    return sum;
}

FourLineFeedbackNetwork::Config shortDelayConfig() {
    FourLineFeedbackNetwork::Config config;
    config.sampleRate = 1000.0;
    config.maxDelaySeconds = 0.1;
    config.delaySeconds = {0.003, 0.005, 0.007, 0.011};
    config.feedback = 0.0F;
    config.damping = 0.0F;
    return config;
}

void testOrthogonalMixPreservesEnergy() {
    const FourLineFeedbackNetwork::LineValues input{1.0F, 0.5F, -0.25F, 0.125F};
    const auto output = FourLineFeedbackNetwork::orthogonalMix(input);
    expect(std::abs(energy(input) - energy(output)) < 1.0e-6F,
           "normalized Hadamard mixing must preserve vector energy");
}

void testEachLineKeepsItsOwnDelayCoordinate() {
    FourLineFeedbackNetwork network(shortDelayConfig());
    const std::array<int, 4> arrivalSamples{3, 5, 7, 11};

    for (int sample = 0; sample <= 11; ++sample) {
        network.process(sample == 0 ? 1.0F : 0.0F);
        const auto& lines = network.lastLineOutputs();
        for (std::size_t line = 0; line < lines.size(); ++line) {
            const float expected = sample == arrivalSamples[line] ? 0.5F : 0.0F;
            expect(std::abs(lines[line] - expected) < 1.0e-6F,
                   "each line must expose the impulse at its configured delay");
        }
    }
}

void testProtectedFeedbackStaysFinite() {
    auto config = shortDelayConfig();
    config.feedback = 1.2F;
    config.damping = 0.2F;
    FourLineFeedbackNetwork network(config);

    float peak = 0.0F;
    for (int sample = 0; sample < 200000; ++sample) {
        const auto frame = network.process(sample == 0 ? 1.0F : 0.0F);
        expect(std::isfinite(frame.left) && std::isfinite(frame.right),
               "stereo return must remain finite");
        peak = std::max({peak, std::abs(frame.left), std::abs(frame.right)});
        for (const float line : network.lastLineOutputs()) {
            expect(std::isfinite(line), "every feedback line must remain finite");
        }
    }
    expect(peak <= 2.0F, "protected feedback return must remain bounded");
}

void testResetClearsRecursiveMemory() {
    auto config = shortDelayConfig();
    config.feedback = 0.9F;
    FourLineFeedbackNetwork network(config);
    for (int sample = 0; sample < 100; ++sample) {
        network.process(sample == 0 ? 1.0F : 0.0F);
    }

    network.reset();
    for (int sample = 0; sample < 100; ++sample) {
        const auto frame = network.process(0.0F);
        expect(std::abs(frame.left) < 1.0e-7F && std::abs(frame.right) < 1.0e-7F,
               "reset must remove all delayed and recursive audio");
    }
}

void testParameterClamping() {
    FourLineFeedbackNetwork network(shortDelayConfig());
    network.setFeedback(9.0F);
    network.setDamping(-1.0F);
    expect(std::abs(network.feedback() - 1.5F) < 1.0e-6F,
           "feedback must clamp to the research ceiling");
    expect(std::abs(network.damping()) < 1.0e-6F,
           "damping must clamp to zero");
}
} // namespace

int main() {
    testOrthogonalMixPreservesEnergy();
    testEachLineKeepsItsOwnDelayCoordinate();
    testProtectedFeedbackStaysFinite();
    testResetClearsRecursiveMemory();
    testParameterClamping();

    if (failures != 0) {
        std::cerr << failures << " test assertion(s) failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "FourLineFeedbackNetwork: all tests passed\n";
    return EXIT_SUCCESS;
}
