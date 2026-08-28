import AVFAudio
import CryptoKit
import Foundation
import XCTest

final class LosslessDecodeBenchmarks: XCTestCase {
    private static let chunkFrames: AVAudioFrameCount = 4_096
    private static let seekPositions: [Double] = [5, 30, 60, 90, 115]

    private final class Results: @unchecked Sendable {
        private let lock = NSLock()
        private(set) var checksums: [UInt64] = []
        private(set) var errors: [String] = []

        func add(checksum: UInt64) {
            lock.lock()
            checksums.append(checksum)
            lock.unlock()
        }

        func add(error: Error) {
            lock.lock()
            errors.append(String(describing: error))
            lock.unlock()
        }
    }

    private enum BenchmarkError: Error {
        case missingResource(String)
        case unsupportedPCMFormat
        case emptyReadBeforeEnd
        case incompleteSlice(expected: AVAudioFramePosition, actual: AVAudioFramePosition)
    }

    private static func resourceURL(extension fileExtension: String) throws -> URL {
        guard let url = Bundle(for: LosslessDecodeBenchmarks.self)
            .url(forResource: "source", withExtension: fileExtension) else {
            throw BenchmarkError.missingResource("source.\(fileExtension)")
        }
        return url
    }

    private static func decodeEntireFile(_ url: URL) throws -> UInt64 {
        let file = try AVAudioFile(
            forReading: url,
            commonFormat: .pcmFormatInt32,
            interleaved: false
        )
        guard let buffer = AVAudioPCMBuffer(
            pcmFormat: file.processingFormat,
            frameCapacity: chunkFrames
        ) else {
            throw BenchmarkError.unsupportedPCMFormat
        }

        var checksum: UInt64 = 0
        while file.framePosition < file.length {
            let remaining = file.length - file.framePosition
            let requested = AVAudioFrameCount(
                min(AVAudioFramePosition(chunkFrames), remaining)
            )
            try file.read(into: buffer, frameCount: requested)
            guard buffer.frameLength > 0 else {
                throw BenchmarkError.emptyReadBeforeEnd
            }
            guard let channels = buffer.int32ChannelData else {
                throw BenchmarkError.unsupportedPCMFormat
            }

            // Touch decoded samples without making hashing dominate the benchmark.
            for channel in 0 ..< Int(buffer.format.channelCount) {
                let samples = channels[channel]
                checksum = checksum &* 1_099_511_628_211
                checksum = checksum &+ UInt64(bitPattern: Int64(samples[0]))
                checksum = checksum &+ UInt64(
                    bitPattern: Int64(samples[Int(buffer.frameLength) - 1])
                )
            }
        }
        return checksum
    }

    private static func sliceDigest(
        _ url: URL,
        positionSeconds: Double,
        durationSeconds: Double = 1
    ) throws -> String {
        let file = try AVAudioFile(
            forReading: url,
            commonFormat: .pcmFormatInt32,
            interleaved: false
        )
        let sampleRate = file.processingFormat.sampleRate
        let startFrame = AVAudioFramePosition((positionSeconds * sampleRate).rounded())
        let requestedFrames = AVAudioFramePosition((durationSeconds * sampleRate).rounded())
        file.framePosition = startFrame

        guard let buffer = AVAudioPCMBuffer(
            pcmFormat: file.processingFormat,
            frameCapacity: chunkFrames
        ) else {
            throw BenchmarkError.unsupportedPCMFormat
        }

        let channelCount = Int(file.processingFormat.channelCount)
        var channelData = [Data](repeating: Data(), count: channelCount)
        var framesRead: AVAudioFramePosition = 0
        while framesRead < requestedFrames {
            let remaining = requestedFrames - framesRead
            let count = AVAudioFrameCount(
                min(AVAudioFramePosition(chunkFrames), remaining)
            )
            try file.read(into: buffer, frameCount: count)
            guard buffer.frameLength > 0,
                  let channels = buffer.int32ChannelData else {
                break
            }

            let byteCount = Int(buffer.frameLength) * MemoryLayout<Int32>.size
            for channel in 0 ..< channelCount {
                channelData[channel].append(
                    Data(bytes: channels[channel], count: byteCount)
                )
            }
            framesRead += AVAudioFramePosition(buffer.frameLength)
        }

        guard framesRead == requestedFrames else {
            throw BenchmarkError.incompleteSlice(
                expected: requestedFrames,
                actual: framesRead
            )
        }
        var hasher = SHA256()
        for data in channelData {
            hasher.update(data: data)
        }
        return hasher.finalize().map { String(format: "%02x", $0) }.joined()
    }

    private func measureSingle(extension fileExtension: String) throws {
        let url = try Self.resourceURL(extension: fileExtension)
        let options = XCTMeasureOptions()
        options.iterationCount = 5

        measure(
            metrics: [XCTClockMetric(), XCTCPUMetric(), XCTMemoryMetric()],
            options: options
        ) {
            do {
                _ = try Self.decodeEntireFile(url)
            } catch {
                XCTFail("\(fileExtension) single decode failed: \(error)")
            }
        }
    }

    private func measureFourTracks(extension fileExtension: String) throws {
        let url = try Self.resourceURL(extension: fileExtension)
        let options = XCTMeasureOptions()
        options.iterationCount = 3

        measure(
            metrics: [XCTClockMetric(), XCTCPUMetric(), XCTMemoryMetric()],
            options: options
        ) {
            let results = Results()
            let queue = OperationQueue()
            queue.maxConcurrentOperationCount = 4

            for _ in 0 ..< 4 {
                queue.addOperation {
                    do {
                        results.add(checksum: try Self.decodeEntireFile(url))
                    } catch {
                        results.add(error: error)
                    }
                }
            }
            queue.waitUntilAllOperationsAreFinished()

            XCTAssertTrue(results.errors.isEmpty, results.errors.joined(separator: "; "))
            XCTAssertEqual(results.checksums.count, 4)
            XCTAssertEqual(Set(results.checksums).count, 1)
        }
    }

    func testSinglePCM() throws { try measureSingle(extension: "wav") }
    func testSingleALAC() throws { try measureSingle(extension: "m4a") }
    func testSingleFLAC() throws { try measureSingle(extension: "flac") }

    func testFourTrackPCM() throws { try measureFourTracks(extension: "wav") }
    func testFourTrackALAC() throws { try measureFourTracks(extension: "m4a") }
    func testFourTrackFLAC() throws { try measureFourTracks(extension: "flac") }

    func testAssetsHaveSameTimeline() throws {
        for fileExtension in ["wav", "m4a", "flac"] {
            let url = try Self.resourceURL(extension: fileExtension)
            let file = try AVAudioFile(forReading: url)
            XCTAssertEqual(file.length, 5_760_000, "source.\(fileExtension) length")
            XCTAssertEqual(file.fileFormat.sampleRate, 48_000, accuracy: 0.001)
            XCTAssertEqual(file.fileFormat.channelCount, 2)
        }
    }

    func testSeekedSamplesMatchPCM() throws {
        let pcm = try Self.resourceURL(extension: "wav")
        let compressed = [
            "ALAC": try Self.resourceURL(extension: "m4a"),
            "FLAC": try Self.resourceURL(extension: "flac")
        ]

        for position in Self.seekPositions {
            let reference = try Self.sliceDigest(pcm, positionSeconds: position)
            for (format, url) in compressed {
                let decoded = try Self.sliceDigest(url, positionSeconds: position)
                XCTAssertEqual(
                    decoded,
                    reference,
                    "\(format) differs from PCM at \(position) seconds"
                )
            }
        }
    }
}
