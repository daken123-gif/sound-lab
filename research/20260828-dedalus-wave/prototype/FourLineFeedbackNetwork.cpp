#include "FourLineFeedbackNetwork.h"

#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace soundlab::research {
namespace {
constexpr float kInputDistribution = 0.5F;
constexpr float kStereoNormalization = 0.70710678118654752440F;
}

FourLineFeedbackNetwork::FourLineFeedbackNetwork(const Config& config)
    : feedback_(config.feedback),
      damping_(config.damping),
      dcBlockerPole_(config.dcBlockerPole) {
    if (!(config.sampleRate > 0.0) || !(config.maxDelaySeconds > 0.0)) {
        throw std::invalid_argument("sample rate and maximum delay must be positive");
    }

    const double maxDelaySamples = std::max(1.0, config.maxDelaySeconds * config.sampleRate);
    bufferSize_ = static_cast<std::size_t>(std::ceil(maxDelaySamples)) + 2U;
    for (auto& buffer : buffers_) {
        buffer.assign(bufferSize_, 0.0F);
    }

    for (std::size_t line = 0; line < delaySamples_.size(); ++line) {
        delaySamples_[line] = std::clamp(
            config.delaySeconds[line] * config.sampleRate, 1.0, maxDelaySamples);
    }
    setFeedback(config.feedback);
    setDamping(config.damping);
    dcBlockerPole_ = std::clamp(config.dcBlockerPole, 0.0F, 0.9999F);
}

FourLineFeedbackNetwork::StereoFrame FourLineFeedbackNetwork::process(float input) noexcept {
    for (std::size_t line = 0; line < lastLineOutputs_.size(); ++line) {
        lastLineOutputs_[line] = readInterpolated(line, delaySamples_[line]);
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
    writeIndex_ = 0;
}

void FourLineFeedbackNetwork::setFeedback(float amount) noexcept {
    feedback_ = std::clamp(amount, 0.0F, 1.5F);
}

void FourLineFeedbackNetwork::setDamping(float amount) noexcept {
    damping_ = std::clamp(amount, 0.0F, 0.999F);
}

float FourLineFeedbackNetwork::feedback() const noexcept {
    return feedback_;
}

float FourLineFeedbackNetwork::damping() const noexcept {
    return damping_;
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
