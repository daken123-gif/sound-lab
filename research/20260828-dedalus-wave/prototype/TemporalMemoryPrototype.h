#pragma once

#include <cstddef>
#include <vector>

namespace soundlab::research {

// Research prototype only: one mono variable-delay cell with a protected
// feedback loop. It intentionally does not implement the proposed four-line
// network, stereo spreading, UI gestures, ducking, or product integration.
class TemporalMemoryPrototype {
public:
    struct Config {
        double sampleRate = 48000.0;
        double maxDelaySeconds = 2.0;
        double initialDelaySeconds = 0.25;
        std::size_t crossfadeSamples = 256;
        float feedback = 0.0F;
        float dcBlockerPole = 0.995F;
    };

    explicit TemporalMemoryPrototype(const Config& config);

    float process(float input) noexcept;
    void reset() noexcept;
    void setDelaySeconds(double seconds) noexcept;
    void setFeedback(float amount) noexcept;

    [[nodiscard]] double delaySeconds() const noexcept;
    [[nodiscard]] float feedback() const noexcept;
    [[nodiscard]] bool isCrossfading() const noexcept;

private:
    [[nodiscard]] double clampDelaySamples(double samples) const noexcept;
    [[nodiscard]] float readInterpolated(double delaySamples) const noexcept;
    [[nodiscard]] float blockDc(float input) noexcept;

    std::vector<float> buffer_;
    std::size_t writeIndex_ = 0;
    double sampleRate_ = 48000.0;
    double maxDelaySamples_ = 1.0;
    double activeDelaySamples_ = 1.0;
    double previousDelaySamples_ = 1.0;
    double targetDelaySamples_ = 1.0;
    std::size_t crossfadeSamples_ = 1;
    std::size_t crossfadePosition_ = 1;
    float feedback_ = 0.0F;
    float dcBlockerPole_ = 0.995F;
    float dcPreviousInput_ = 0.0F;
    float dcPreviousOutput_ = 0.0F;
};

} // namespace soundlab::research
