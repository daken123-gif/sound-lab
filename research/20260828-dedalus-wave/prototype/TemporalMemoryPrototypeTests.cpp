#include "TemporalMemoryPrototype.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

using soundlab::research::TemporalMemoryPrototype;

namespace {
int failures = 0;

void expect(bool condition, const std::string& message) {
    if (!condition) {
        ++failures;
        std::cerr << "FAIL: " << message << '\n';
    }
}

void testImpulseDelay() {
    TemporalMemoryPrototype::Config config;
    config.sampleRate = 1000.0;
    config.maxDelaySeconds = 0.1;
    config.initialDelaySeconds = 0.008;
    config.crossfadeSamples = 8;
    config.feedback = 0.0F;
    TemporalMemoryPrototype memory(config);

    std::vector<float> output(20, 0.0F);
    for (std::size_t i = 0; i < output.size(); ++i) {
        output[i] = memory.process(i == 0U ? 1.0F : 0.0F);
    }

    expect(std::abs(output[8] - 1.0F) < 1.0e-6F,
           "an impulse must appear at the configured delay");
    expect(std::abs(output[7]) < 1.0e-6F, "the impulse must not arrive early");
}

void testEqualPowerJumpHasNoHole() {
    TemporalMemoryPrototype::Config config;
    config.sampleRate = 1000.0;
    config.maxDelaySeconds = 0.1;
    config.initialDelaySeconds = 0.004;
    config.crossfadeSamples = 32;
    TemporalMemoryPrototype memory(config);

    for (int i = 0; i < 120; ++i) {
        memory.process(1.0F);
    }
    memory.setDelaySeconds(0.017);

    float minimum = std::numeric_limits<float>::max();
    float maximum = 0.0F;
    for (int i = 0; i < 32; ++i) {
        const float value = memory.process(1.0F);
        minimum = std::min(minimum, value);
        maximum = std::max(maximum, value);
    }

    expect(minimum > 0.99F, "dual-head crossfade must not create an amplitude hole");
    expect(maximum <= 1.415F, "equal-power crossfade must stay within sqrt(2)");
    expect(!memory.isCrossfading(), "the transition must finish at the requested length");
    expect(std::abs(memory.delaySeconds() - 0.017) < 1.0e-9,
           "the target delay must become active");
}

void testFractionalDelayInterpolation() {
    TemporalMemoryPrototype::Config config;
    config.sampleRate = 1000.0;
    config.maxDelaySeconds = 0.1;
    config.initialDelaySeconds = 0.0015;
    config.feedback = 0.0F;
    TemporalMemoryPrototype memory(config);

    const float first = memory.process(1.0F);
    const float second = memory.process(0.0F);
    const float third = memory.process(0.0F);
    expect(std::abs(first) < 1.0e-6F, "fractional delay must not output before history exists");
    expect(std::abs(second - 0.5F) < 1.0e-6F, "linear interpolation must split the impulse");
    expect(std::abs(third - 0.5F) < 1.0e-6F, "linear interpolation must preserve its second half");
}

void testProtectedHighFeedbackStaysFinite() {
    TemporalMemoryPrototype::Config config;
    config.sampleRate = 1000.0;
    config.maxDelaySeconds = 0.1;
    config.initialDelaySeconds = 0.007;
    config.feedback = 1.2F;
    TemporalMemoryPrototype memory(config);

    float peak = 0.0F;
    for (int i = 0; i < 100000; ++i) {
        const float output = memory.process(i == 0 ? 1.0F : 0.0F);
        expect(std::isfinite(output), "feedback loop must never produce NaN or infinity");
        peak = std::max(peak, std::abs(output));
    }
    expect(peak <= 1.01F, "soft clipping must bound the recursive signal");
}

void testParameterClamping() {
    TemporalMemoryPrototype::Config config;
    config.sampleRate = 1000.0;
    config.maxDelaySeconds = 0.1;
    config.initialDelaySeconds = 0.01;
    TemporalMemoryPrototype memory(config);

    memory.setDelaySeconds(-1.0);
    expect(std::abs(memory.delaySeconds() - 0.001) < 1.0e-9,
           "delay must clamp to one sample");
    memory.setDelaySeconds(10.0);
    expect(std::abs(memory.delaySeconds() - 0.1) < 1.0e-9,
           "delay must clamp to the configured maximum");
    memory.setFeedback(9.0F);
    expect(std::abs(memory.feedback() - 1.5F) < 1.0e-6F,
           "feedback must clamp to the research ceiling");
}
} // namespace

int main() {
    testImpulseDelay();
    testEqualPowerJumpHasNoHole();
    testFractionalDelayInterpolation();
    testProtectedHighFeedbackStaysFinite();
    testParameterClamping();

    if (failures != 0) {
        std::cerr << failures << " test assertion(s) failed\n";
        return EXIT_FAILURE;
    }
    std::cout << "TemporalMemoryPrototype: all tests passed\n";
    return EXIT_SUCCESS;
}
