#pragma once

#include <array>
#include <cstddef>
#include <vector>

namespace soundlab::research {

// Project-specific four-line FDN candidate. Four is an experiment size, not a
// claim about the unpublished internal topology of Dedalus.
class FourLineFeedbackNetwork {
public:
    using LineValues = std::array<float, 4>;

    struct StereoFrame {
        float left = 0.0F;
        float right = 0.0F;
    };

    struct Config {
        double sampleRate = 48000.0;
        double maxDelaySeconds = 2.0;
        std::array<double, 4> delaySeconds{0.029, 0.037, 0.041, 0.053};
        std::size_t crossfadeSamples = 256;
        float feedback = 0.75F;
        float damping = 0.25F;
        float dcBlockerPole = 0.995F;
    };

    explicit FourLineFeedbackNetwork(const Config& config);

    StereoFrame process(float input) noexcept;
    void reset() noexcept;
    void setFeedback(float amount) noexcept;
    void setDamping(float amount) noexcept;
    void setLineDelaySeconds(std::size_t line, double seconds) noexcept;

    [[nodiscard]] float feedback() const noexcept;
    [[nodiscard]] float damping() const noexcept;
    [[nodiscard]] double lineDelaySeconds(std::size_t line) const noexcept;
    [[nodiscard]] bool isLineCrossfading(std::size_t line) const noexcept;
    [[nodiscard]] const LineValues& lastLineOutputs() const noexcept;

    // Normalized 4x4 Hadamard transform. The factor 1/2 makes the matrix
    // orthogonal, so the linear mixing stage preserves vector energy.
    [[nodiscard]] static LineValues orthogonalMix(const LineValues& input) noexcept;

private:
    [[nodiscard]] float readInterpolated(std::size_t line, double delaySamples) const noexcept;
    [[nodiscard]] float readLine(std::size_t line) noexcept;
    [[nodiscard]] float blockDc(std::size_t line, float input) noexcept;

    std::array<std::vector<float>, 4> buffers_;
    std::array<double, 4> activeDelaySamples_{};
    std::array<double, 4> previousDelaySamples_{};
    std::array<double, 4> targetDelaySamples_{};
    std::array<std::size_t, 4> crossfadePositions_{};
    LineValues lowpassState_{};
    LineValues dcPreviousInput_{};
    LineValues dcPreviousOutput_{};
    LineValues lastLineOutputs_{};
    std::size_t writeIndex_ = 0;
    std::size_t bufferSize_ = 0;
    std::size_t crossfadeSamples_ = 1;
    double sampleRate_ = 48000.0;
    double maxDelaySamples_ = 1.0;
    float feedback_ = 0.75F;
    float damping_ = 0.25F;
    float dcBlockerPole_ = 0.995F;
};

} // namespace soundlab::research
