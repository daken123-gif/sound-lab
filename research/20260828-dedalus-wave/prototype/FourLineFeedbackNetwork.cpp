#include "FourLineFeedbackNetwork.h"

#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace soundlab::research {
namespace {
constexpr float kInputDistribution = 0.5F;
constexpr float kStereoNormalization = 0.70710678118654752440F;
constexpr double kHalfPi = 1.57079632679489661923;
}

FourLineFeedbackNetwork::FourLineFeedbackNetwork(const Config& config)
    : crossfadeSamples_(std::max<std::size_t>(1, config.crossfadeSamples)),
      sampleRate_(config.sampleRate),
      feedback_(config.feedback),
      damping_(config.damping),
      dcBlockerPole_(config.dcBlockerPole) {
    if (!(config.sampleRate > 0.0) || !(config.maxDelaySeconds > 0.0)) {
        throw std::invalid_argument("sample rate and maximum delay must be positive");
    }

    maxDelaySamples_ = std::max(1.0, config.maxDelaySeconds * config.sampleRate);
    bufferSize_ = static_cast<std::size_t>(std::ceil(maxDelaySamples_)) + 2U;
    for (auto& buffer : buffers_) {
        buffer.assign(bufferSize_, 0.0F);
    }

    for (std::size_t line = 0; line < activeDelaySamples_.size(); ++line) {
        activeDelaySamples_[line] = std::clamp(
            config.delaySeconds[line] * config.sampleRate, 1.0, maxDelaySamples_);
        previousDelaySamples_[line] = activeDelaySamples_[line];
        targetDelaySamples_[line] = activeDelaySamples_[line];
        crossfadePositions_[line] = crossfadeSamples_;
    }
    setFeedback(config.feedback);
    setDamping(config.damping);
    dcBlockerPole_ = std::clamp(config.dcBlockerPole, 0.0F, 0.9999F);
}

FourLineFeedbackNetwork::StereoFrame FourLineFeedbackNetwork::process(float input) noexcept {
    for (std::size_t line = 0; line < lastLineOutputs_.size(); ++line) {
        lastLineOutputs_[line] = readLine(line);
    }

    const LineValues mixed = orthogonalMix(lastLineOutputs_);
    for (std::size_t line = 0; line < buffers_.size(); ++line) {
        lowpassState_[line] = damping_ * lowpassState_[line] +
                              (1.0F - damping_) * mixed[line];
        const float recursive = std::tanh(
            blockDc(line, lowpassState_[line] * feedback_));
        buffers_[line][writeIndex_] = input * kInputDistribution + recursive;
    }

    writeIndex_ = (writeIndex_ + 1U) % bufferSize_;
    return {
        (lastLineOutputs_[0] + lastLineOutputs_[2]) * kStereoNormalization,
        (lastLineOutputs_[1] + lastLineOutputs_[3]) * kStereoNormalization,
    };
}

void FourLineFeedbackNetwork::reset() noexcept {
    for (auto& buffer : buffers_) {
        std::fill(buffer.begin(), buffer.end(), 0.0F);
    }
    lowpassState_.fill(0.0F);
    dcPreviousInput_.fill(0.0F);
    dcPreviousOutput_.fill(0.0F);
    lastLineOutputs_.fill(0.0F);
    previousDelaySamples_ = activeDelaySamples_;
    targetDelaySamples_ = activeDelaySamples_;
    crossfadePositions_.fill(crossfadeSamples_);
    writeIndex_ = 0;
}

void FourLineFeedbackNetwork::setFeedback(float amount) noexcept {
    feedback_ = std::clamp(amount, 0.0F, 1.5F);
}

void FourLineFeedbackNetwork::setDamping(float amount) noexcept {
    damping_ = std::clamp(amount, 0.0F, 0.999F);
}

void FourLineFeedbackNetwork::setLineDelaySeconds(
    std::size_t line, double seconds) noexcept {
    if (line >= targetDelaySamples_.size()) {
        return;
    }
    const double nextDelay = std::clamp(seconds * sampleRate_, 1.0, maxDelaySamples_);
    if (std::abs(nextDelay - targetDelaySamples_[line]) < 1.0e-9) {
        return;
    }

    // A mid-fade retarget restarts from the last fully active head. Its click
    // behavior is intentionally left as a separate unresolved experiment.
    previousDelaySamples_[line] = activeDelaySamples_[line];
    targetDelaySamples_[line] = nextDelay;
    crossfadePositions_[line] = 0;
}

float FourLineFeedbackNetwork::feedback() const noexcept {
    return feedback_;
}

float FourLineFeedbackNetwork::damping() const noexcept {
    return damping_;
}

double FourLineFeedbackNetwork::lineDelaySeconds(std::size_t line) const noexcept {
    if (line >= targetDelaySamples_.size()) {
        return 0.0;
    }
    return targetDelaySamples_[line] / sampleRate_;
}

bool FourLineFeedbackNetwork::isLineCrossfading(std::size_t line) const noexcept {
    return line < crossfadePositions_.size() &&
           crossfadePositions_[line] < crossfadeSamples_;
}

const FourLineFeedbackNetwork::LineValues&
FourLineFeedbackNetwork::lastLineOutputs() const noexcept {
    return lastLineOutputs_;
}

FourLineFeedbackNetwork::LineValues
FourLineFeedbackNetwork::orthogonalMix(const LineValues& input) noexcept {
    return {
        0.5F * (input[0] + input[1] + input[2] + input[3]),
        0.5F * (input[0] - input[1] + input[2] - input[3]),
        0.5F * (input[0] + input[1] - input[2] - input[3]),
        0.5F * (input[0] - input[1] - input[2] + input[3]),
    };
}

float FourLineFeedbackNetwork::readLine(std::size_t line) noexcept {
    if (crossfadePositions_[line] >= crossfadeSamples_) {
        return readInterpolated(line, activeDelaySamples_[line]);
    }

    const double phase = static_cast<double>(crossfadePositions_[line] + 1U) /
                         static_cast<double>(crossfadeSamples_);
    const float oldWeight = static_cast<float>(std::cos(phase * kHalfPi));
    const float newWeight = static_cast<float>(std::sin(phase * kHalfPi));
    const float output = oldWeight * readInterpolated(line, previousDelaySamples_[line]) +
                         newWeight * readInterpolated(line, targetDelaySamples_[line]);

    ++crossfadePositions_[line];
    if (crossfadePositions_[line] >= crossfadeSamples_) {
        activeDelaySamples_[line] = targetDelaySamples_[line];
    }
    return output;
}

float FourLineFeedbackNetwork::readInterpolated(
    std::size_t line, double delaySamples) const noexcept {
    double readPosition = static_cast<double>(writeIndex_) - delaySamples;
    const double size = static_cast<double>(bufferSize_);
    while (readPosition < 0.0) {
        readPosition += size;
    }
    while (readPosition >= size) {
        readPosition -= size;
    }

    const auto index0 = static_cast<std::size_t>(std::floor(readPosition));
    const auto index1 = (index0 + 1U) % bufferSize_;
    const float fraction = static_cast<float>(readPosition - std::floor(readPosition));
    return buffers_[line][index0] +
           (buffers_[line][index1] - buffers_[line][index0]) * fraction;
}

float FourLineFeedbackNetwork::blockDc(std::size_t line, float input) noexcept {
    const float output = input - dcPreviousInput_[line] +
                         dcBlockerPole_ * dcPreviousOutput_[line];
    dcPreviousInput_[line] = input;
    dcPreviousOutput_[line] = output;
    return output;
}

} // namespace soundlab::research
