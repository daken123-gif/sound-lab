#include "TemporalMemoryPrototype.h"

#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace soundlab::research {
namespace {
constexpr double kHalfPi = 1.57079632679489661923;
}

TemporalMemoryPrototype::TemporalMemoryPrototype(const Config& config)
    : sampleRate_(config.sampleRate),
      crossfadeSamples_(std::max<std::size_t>(1, config.crossfadeSamples)),
      feedback_(config.feedback),
      dcBlockerPole_(config.dcBlockerPole) {
    if (!(sampleRate_ > 0.0) || !(config.maxDelaySeconds > 0.0)) {
        throw std::invalid_argument("sample rate and maximum delay must be positive");
    }

    maxDelaySamples_ = std::max(1.0, config.maxDelaySeconds * sampleRate_);
    buffer_.assign(static_cast<std::size_t>(std::ceil(maxDelaySamples_)) + 2U, 0.0F);
    activeDelaySamples_ = clampDelaySamples(config.initialDelaySeconds * sampleRate_);
    previousDelaySamples_ = activeDelaySamples_;
    targetDelaySamples_ = activeDelaySamples_;
    crossfadePosition_ = crossfadeSamples_;
    setFeedback(config.feedback);
    dcBlockerPole_ = std::clamp(config.dcBlockerPole, 0.0F, 0.9999F);
}

float TemporalMemoryPrototype::process(float input) noexcept {
    float delayed = 0.0F;

    if (crossfadePosition_ < crossfadeSamples_) {
        const double phase = static_cast<double>(crossfadePosition_ + 1U) /
                             static_cast<double>(crossfadeSamples_);
        const float oldWeight = static_cast<float>(std::cos(phase * kHalfPi));
        const float newWeight = static_cast<float>(std::sin(phase * kHalfPi));
        delayed = oldWeight * readInterpolated(previousDelaySamples_) +
                  newWeight * readInterpolated(targetDelaySamples_);

        ++crossfadePosition_;
        if (crossfadePosition_ >= crossfadeSamples_) {
            activeDelaySamples_ = targetDelaySamples_;
        }
    } else {
        delayed = readInterpolated(activeDelaySamples_);
    }

    const float protectedFeedback = std::tanh(blockDc(delayed * feedback_));
    buffer_[writeIndex_] = input + protectedFeedback;
    writeIndex_ = (writeIndex_ + 1U) % buffer_.size();
    return delayed;
}

void TemporalMemoryPrototype::reset() noexcept {
    std::fill(buffer_.begin(), buffer_.end(), 0.0F);
    writeIndex_ = 0;
    previousDelaySamples_ = activeDelaySamples_;
    targetDelaySamples_ = activeDelaySamples_;
    crossfadePosition_ = crossfadeSamples_;
    dcPreviousInput_ = 0.0F;
    dcPreviousOutput_ = 0.0F;
}

void TemporalMemoryPrototype::setDelaySeconds(double seconds) noexcept {
    const double nextDelay = clampDelaySamples(seconds * sampleRate_);
    if (std::abs(nextDelay - targetDelaySamples_) < 1.0e-9) {
        return;
    }

    // A new jump begins from the last fully active head. This keeps the
    // implementation deterministic; retargeting mid-fade is a later test.
    previousDelaySamples_ = activeDelaySamples_;
    targetDelaySamples_ = nextDelay;
    crossfadePosition_ = 0;
}

void TemporalMemoryPrototype::setFeedback(float amount) noexcept {
    feedback_ = std::clamp(amount, 0.0F, 1.5F);
}

double TemporalMemoryPrototype::delaySeconds() const noexcept {
    return targetDelaySamples_ / sampleRate_;
}

float TemporalMemoryPrototype::feedback() const noexcept {
    return feedback_;
}

bool TemporalMemoryPrototype::isCrossfading() const noexcept {
    return crossfadePosition_ < crossfadeSamples_;
}

double TemporalMemoryPrototype::clampDelaySamples(double samples) const noexcept {
    return std::clamp(samples, 1.0, maxDelaySamples_);
}

float TemporalMemoryPrototype::readInterpolated(double delaySamples) const noexcept {
    double readPosition = static_cast<double>(writeIndex_) - delaySamples;
    const double bufferSize = static_cast<double>(buffer_.size());
    while (readPosition < 0.0) {
        readPosition += bufferSize;
    }
    while (readPosition >= bufferSize) {
        readPosition -= bufferSize;
    }

    const auto index0 = static_cast<std::size_t>(std::floor(readPosition));
    const auto index1 = (index0 + 1U) % buffer_.size();
    const float fraction = static_cast<float>(readPosition - std::floor(readPosition));
    return buffer_[index0] + (buffer_[index1] - buffer_[index0]) * fraction;
}

float TemporalMemoryPrototype::blockDc(float input) noexcept {
    const float output = input - dcPreviousInput_ + dcBlockerPole_ * dcPreviousOutput_;
    dcPreviousInput_ = input;
    dcPreviousOutput_ = output;
    return output;
}

} // namespace soundlab::research
