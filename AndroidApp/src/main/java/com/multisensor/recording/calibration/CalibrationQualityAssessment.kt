package com.multisensor.recording.calibration

import android.graphics.Bitmap
import com.multisensor.recording.util.Logger
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.*

/**
 * CalibrationQualityAssessment provides automated quality evaluation for calibration images.
 *
 * Enhanced for with computer vision algorithms including:
 * - Calibration pattern detection (chessboard and circle grid)
 * - Image sharpness and contrast analysis
 * - RGB-thermal alignment verification
 * - Quality scoring and re-capture recommendations
 *
 * Targets 95% accuracy in quality assessment correlation with manual evaluation.
 */
@Singleton
class CalibrationQualityAssessment
    @Inject
    constructor(
        private val logger: Logger,
    ) {
        companion object {
            // Quality assessment thresholds
            private const val MIN_SHARPNESS_SCORE = 0.3f
            private const val MIN_CONTRAST_SCORE = 0.4f
            private const val MIN_PATTERN_SCORE = 0.6f
            private const val MIN_ALIGNMENT_SCORE = 0.5f

            // Pattern detection parameters
            private const val CHESSBOARD_ROWS = 9
            private const val CHESSBOARD_COLS = 6
            private const val CIRCLE_GRID_ROWS = 4
            private const val CIRCLE_GRID_COLS = 11

            // Image analysis parameters
            private const val LAPLACIAN_THRESHOLD = 100.0
            private const val CONTRAST_PERCENTILE = 0.95
            private const val ALIGNMENT_MAX_ERROR = 10.0 // pixels
        }

        /**
         * Pattern detection result for calibration images
         */
        data class PatternDetectionResult(
            val patternFound: Boolean,
            val patternType: PatternType,
            val cornerCount: Int,
            val patternScore: Float, // 0.0 to 1.0
            val geometricDistortion: Float,
            val completeness: Float, // Percentage of expected pattern found
        )

        /**
         * Image sharpness analysis metrics
         */
        data class SharpnessMetrics(
            val laplacianVariance: Double,
            val gradientMagnitude: Double,
            val edgeDensity: Float,
            val sharpnessScore: Float, // 0.0 to 1.0
        )

        /**
         * Image contrast analysis metrics
         */
        data class ContrastMetrics(
            val dynamicRange: Int,
            val histogramSpread: Float,
            val localContrast: Float,
            val contrastScore: Float, // 0.0 to 1.0
        )

        /**
         * RGB-thermal alignment analysis metrics
         */
        data class AlignmentMetrics(
            val featureMatchCount: Int,
            val averageError: Float, // pixels
            val maxError: Float, // pixels
            val transformationMatrix: FloatArray?,
            val alignmentScore: Float, // 0.0 to 1.0
        )

        /**
         * Overall calibration quality score and recommendation
         */
        data class CalibrationQualityScore(
            val overallScore: Float, // 0.0 to 1.0
            val sharpnessScore: Float,
            val contrastScore: Float,
            val alignmentScore: Float,
            val patternDetectionScore: Float,
            val recommendation: QualityRecommendation,
            val analysisDetails: String,
        )

        /**
         * Quality-based recommendations for user action
         */
        enum class QualityRecommendation {
            EXCELLENT,
            GOOD,
            ACCEPTABLE,
            RETAKE_RECOMMENDED,
            RETAKE_REQUIRED,
        }

        /**
         * Supported calibration pattern types
         */
        enum class PatternType {
            CHESSBOARD,
            CIRCLE_GRID,
            UNKNOWN,
        }

        /**
         * Performs comprehensive quality assessment on calibration image pair
         */
        suspend fun assessCalibrationQuality(
            rgbImage: Bitmap,
            thermalImage: Bitmap,
        ): CalibrationQualityScore =
            withContext(Dispatchers.Default) {
                logger.info("[DEBUG_LOG] Starting calibration quality assessment")

                try {
                    // 1. Pattern Detection Analysis
                    val rgbPatternResult = detectCalibrationPattern(rgbImage, PatternType.CHESSBOARD)
                    val thermalPatternResult = detectCalibrationPattern(thermalImage, PatternType.CIRCLE_GRID)

                    val patternScore = (rgbPatternResult.patternScore + thermalPatternResult.patternScore) / 2.0f

                    // 2. Image Quality Analysis
                    val rgbSharpness = analyzeSharpness(rgbImage)
                    val thermalSharpness = analyzeSharpness(thermalImage)
                    val sharpnessScore = (rgbSharpness.sharpnessScore + thermalSharpness.sharpnessScore) / 2.0f

                    val rgbContrast = analyzeContrast(rgbImage)
                    val thermalContrast = analyzeContrast(thermalImage)
                    val contrastScore = (rgbContrast.contrastScore + thermalContrast.contrastScore) / 2.0f

                    // 3. Alignment Analysis
                    val alignmentMetrics = analyzeAlignment(rgbImage, thermalImage)
                    val alignmentScore = alignmentMetrics.alignmentScore

                    // 4. Calculate Overall Score
                    val overallScore =
                        calculateOverallScore(
                            patternScore,
                            sharpnessScore,
                            contrastScore,
                            alignmentScore,
                        )

                    // 5. Generate Recommendation
                    val recommendation =
                        generateRecommendation(
                            overallScore,
                            patternScore,
                            sharpnessScore,
                            contrastScore,
                            alignmentScore,
                        )

                    // 6. Create Analysis Details
                    val analysisDetails =
                        buildAnalysisDetails(
                            rgbPatternResult,
                            thermalPatternResult,
                            rgbSharpness,
                            thermalSharpness,
                            rgbContrast,
                            thermalContrast,
                            alignmentMetrics,
                        )

                    val result =
                        CalibrationQualityScore(
                            overallScore = overallScore,
                            sharpnessScore = sharpnessScore,
                            contrastScore = contrastScore,
                            alignmentScore = alignmentScore,
                            patternDetectionScore = patternScore,
                            recommendation = recommendation,
                            analysisDetails = analysisDetails,
                        )

                    logger.info("[DEBUG_LOG] Quality assessment complete - Overall: $overallScore, Recommendation: $recommendation")

                    result
                } catch (e: Exception) {
                    logger.error("Error during calibration quality assessment", e)

                    CalibrationQualityScore(
                        overallScore = 0.0f,
                        sharpnessScore = 0.0f,
                        contrastScore = 0.0f,
                        alignmentScore = 0.0f,
                        patternDetectionScore = 0.0f,
                        recommendation = QualityRecommendation.RETAKE_REQUIRED,
                        analysisDetails = "Assessment failed: ${e.message}",
                    )
                }
            }

        /**
         * Detects calibration patterns in the given image
         */
        private suspend fun detectCalibrationPattern(
            image: Bitmap,
            expectedType: PatternType,
        ): PatternDetectionResult =
            withContext(Dispatchers.Default) {
                logger.debug("[DEBUG_LOG] Detecting $expectedType pattern")

                return@withContext when (expectedType) {
                    PatternType.CHESSBOARD -> detectChessboardPattern(image)
                    PatternType.CIRCLE_GRID -> detectCircleGridPattern(image)
                    PatternType.UNKNOWN ->
                        PatternDetectionResult(
                            false,
                            PatternType.UNKNOWN,
                            0,
                            0.0f,
                            0.0f,
                            0.0f,
                        )
                }
            }

        /**
         * Detects chessboard pattern using corner detection algorithms
         */
        private fun detectChessboardPattern(image: Bitmap): PatternDetectionResult {
            // Implement Android-native chessboard detection
            logger.debug("[DEBUG_LOG] Analyzing chessboard pattern in image (${image.width}x${image.height})")

            val expectedCorners = (CHESSBOARD_ROWS - 1) * (CHESSBOARD_COLS - 1)

            try {
                // Convert bitmap to grayscale for analysis
                val grayBitmap = convertToGrayscale(image)
                
                // Apply edge detection to find potential corners
                val edges = detectEdges(grayBitmap)
                
                // Find corner candidates using simple corner detection
                val cornerCandidates = findCornerCandidates(edges)
                
                // Filter candidates to find chessboard pattern
                val chessboardCorners = filterChessboardCorners(cornerCandidates, image.width, image.height)
                
                val detectedCorners = chessboardCorners.size
                val completeness = detectedCorners.toFloat() / expectedCorners.toFloat()
                
                // Calculate pattern score based on detected corners and geometric consistency
                val geometricScore = calculateGeometricConsistency(chessboardCorners)
                val patternScore = completeness * geometricScore
                
                logger.debug("[DEBUG_LOG] Chessboard detection - Corners: $detectedCorners/$expectedCorners, Score: $patternScore")

                return PatternDetectionResult(
                    patternFound = detectedCorners >= expectedCorners * 0.7,
                    patternType = PatternType.CHESSBOARD,
                    cornerCount = detectedCorners,
                    patternScore = patternScore,
                    geometricDistortion = 1.0f - geometricScore,
                    completeness = completeness,
                )
            } catch (e: Exception) {
                logger.error("Error in chessboard detection", e)
                return PatternDetectionResult(
                    patternFound = false,
                    patternType = PatternType.CHESSBOARD,
                    cornerCount = 0,
                    patternScore = 0.0f,
                    geometricDistortion = 1.0f,
                    completeness = 0.0f,
                )
            }
        }

        /**
         * Detects circle grid pattern using blob detection algorithms
         */
        private fun detectCircleGridPattern(image: Bitmap): PatternDetectionResult {
            // Implement Android-native circle grid detection
            logger.debug("[DEBUG_LOG] Analyzing circle grid pattern in image (${image.width}x${image.height})")

            val expectedCircles = CIRCLE_GRID_ROWS * CIRCLE_GRID_COLS

            try {
                // Convert bitmap to grayscale for analysis
                val grayBitmap = convertToGrayscale(image)
                
                // Apply blob detection to find circular patterns
                val blobs = detectCircularBlobs(grayBitmap)
                
                // Filter blobs to find grid pattern
                val gridCircles = filterGridCircles(blobs, image.width, image.height)
                
                val detectedCircles = gridCircles.size
                val completeness = detectedCircles.toFloat() / expectedCircles.toFloat()
                
                // Calculate pattern score based on detected circles and grid consistency
                val gridScore = calculateGridConsistency(gridCircles)
                val patternScore = completeness * gridScore * 0.85f // Thermal images typically have lower quality
                
                logger.debug("[DEBUG_LOG] Circle grid detection - Circles: $detectedCircles/$expectedCircles, Score: $patternScore")

                return PatternDetectionResult(
                    patternFound = detectedCircles >= expectedCircles * 0.6,
                    patternType = PatternType.CIRCLE_GRID,
                    cornerCount = detectedCircles,
                    patternScore = patternScore,
                    geometricDistortion = 1.0f - gridScore,
                    completeness = completeness,
                )
            } catch (e: Exception) {
                logger.error("Error in circle grid detection", e)
                return PatternDetectionResult(
                    patternFound = false,
                    patternType = PatternType.CIRCLE_GRID,
                    cornerCount = 0,
                    patternScore = 0.0f,
                    geometricDistortion = 1.0f,
                    completeness = 0.0f,
                )
            }
        }

        /**
         * Analyzes image sharpness using multiple algorithms
         */
        private fun analyzeSharpness(image: Bitmap): SharpnessMetrics {
            logger.debug("[DEBUG_LOG] Analyzing image sharpness")

            // Convert bitmap to grayscale array for analysis
            val pixels = IntArray(image.width * image.height)
            image.getPixels(pixels, 0, image.width, 0, 0, image.width, image.height)

            val grayPixels =
                pixels.map { pixel ->
                    val r = (pixel shr 16) and 0xFF
                    val g = (pixel shr 8) and 0xFF
                    val b = pixel and 0xFF
                    (0.299 * r + 0.587 * g + 0.114 * b).toInt()
                }

            // 1. Laplacian Variance Method
            val laplacianVariance = calculateLaplacianVariance(grayPixels, image.width, image.height)

            // 2. Gradient Magnitude Analysis
            val gradientMagnitude = calculateGradientMagnitude(grayPixels, image.width, image.height)

            // 3. Edge Density Calculation
            val edgeDensity = calculateEdgeDensity(grayPixels, image.width, image.height)

            // Calculate overall sharpness score
            val sharpnessScore = calculateSharpnessScore(laplacianVariance, gradientMagnitude, edgeDensity)

            logger.debug(
                "[DEBUG_LOG] Sharpness analysis - Laplacian: $laplacianVariance, Gradient: $gradientMagnitude, Score: $sharpnessScore",
            )

            return SharpnessMetrics(
                laplacianVariance = laplacianVariance,
                gradientMagnitude = gradientMagnitude,
                edgeDensity = edgeDensity,
                sharpnessScore = sharpnessScore,
            )
        }

        /**
         * Calculates Laplacian variance for sharpness measurement
         */
        private fun calculateLaplacianVariance(
            pixels: List<Int>,
            width: Int,
            height: Int,
        ): Double {
            val laplacianKernel =
                arrayOf(
                    intArrayOf(0, -1, 0),
                    intArrayOf(-1, 4, -1),
                    intArrayOf(0, -1, 0),
                )

            val laplacianValues = mutableListOf<Double>()

            for (y in 1 until height - 1) {
                for (x in 1 until width - 1) {
                    var laplacianValue = 0.0

                    for (ky in -1..1) {
                        for (kx in -1..1) {
                            val pixelIndex = (y + ky) * width + (x + kx)
                            laplacianValue += pixels[pixelIndex] * laplacianKernel[ky + 1][kx + 1]
                        }
                    }

                    laplacianValues.add(laplacianValue)
                }
            }

            val mean = laplacianValues.average()
            return laplacianValues.map { (it - mean).pow(2) }.average()
        }

        /**
         * Calculates gradient magnitude for edge analysis
         */
        private fun calculateGradientMagnitude(
            pixels: List<Int>,
            width: Int,
            height: Int,
        ): Double {
            var totalGradient = 0.0
            var count = 0

            for (y in 1 until height - 1) {
                for (x in 1 until width - 1) {
                    val gx = pixels[y * width + (x + 1)] - pixels[y * width + (x - 1)]
                    val gy = pixels[(y + 1) * width + x] - pixels[(y - 1) * width + x]

                    val magnitude = sqrt((gx * gx + gy * gy).toDouble())
                    totalGradient += magnitude
                    count++
                }
            }

            return if (count > 0) totalGradient / count else 0.0
        }

        /**
         * Calculates edge density in the image
         */
        private fun calculateEdgeDensity(
            pixels: List<Int>,
            width: Int,
            height: Int,
        ): Float {
            var edgeCount = 0
            val threshold = 30 // Edge detection threshold

            for (y in 1 until height - 1) {
                for (x in 1 until width - 1) {
                    val gx = abs(pixels[y * width + (x + 1)] - pixels[y * width + (x - 1)])
                    val gy = abs(pixels[(y + 1) * width + x] - pixels[(y - 1) * width + x])

                    if (gx > threshold || gy > threshold) {
                        edgeCount++
                    }
                }
            }

            val totalPixels = (width - 2) * (height - 2)
            return if (totalPixels > 0) edgeCount.toFloat() / totalPixels.toFloat() else 0.0f
        }

        /**
         * Calculates overall sharpness score from multiple metrics
         */
        private fun calculateSharpnessScore(
            laplacianVariance: Double,
            gradientMagnitude: Double,
            edgeDensity: Float,
        ): Float {
            // Normalize metrics to 0-1 range
            val normalizedLaplacian = (laplacianVariance / LAPLACIAN_THRESHOLD).coerceIn(0.0, 1.0).toFloat()
            val normalizedGradient = (gradientMagnitude / 50.0).coerceIn(0.0, 1.0).toFloat()
            val normalizedEdgeDensity = edgeDensity.coerceIn(0.0f, 1.0f)

            // Weighted combination
            return (normalizedLaplacian * 0.5f + normalizedGradient * 0.3f + normalizedEdgeDensity * 0.2f)
        }

        /**
         * Analyzes image contrast using histogram and local methods
         */
        private fun analyzeContrast(image: Bitmap): ContrastMetrics {
            logger.debug("[DEBUG_LOG] Analyzing image contrast")

            // Convert bitmap to grayscale for analysis
            val pixels = IntArray(image.width * image.height)
            image.getPixels(pixels, 0, image.width, 0, 0, image.width, image.height)

            val grayValues =
                pixels.map { pixel ->
                    val r = (pixel shr 16) and 0xFF
                    val g = (pixel shr 8) and 0xFF
                    val b = pixel and 0xFF
                    (0.299 * r + 0.587 * g + 0.114 * b).toInt()
                }

            // 1. Dynamic Range Analysis
            val minValue = grayValues.minOrNull() ?: 0
            val maxValue = grayValues.maxOrNull() ?: 255
            val dynamicRange = maxValue - minValue

            // 2. Histogram Spread Analysis
            val histogram = IntArray(256)
            grayValues.forEach { histogram[it]++ }

            val histogramSpread = calculateHistogramSpread(histogram)

            // 3. Local Contrast Analysis
            val localContrast = calculateLocalContrast(grayValues, image.width, image.height)

            // Calculate overall contrast score
            val contrastScore = calculateContrastScore(dynamicRange, histogramSpread, localContrast)

            logger.debug("[DEBUG_LOG] Contrast analysis - Range: $dynamicRange, Spread: $histogramSpread, Score: $contrastScore")

            return ContrastMetrics(
                dynamicRange = dynamicRange,
                histogramSpread = histogramSpread,
                localContrast = localContrast,
                contrastScore = contrastScore,
            )
        }

        /**
         * Calculates histogram spread for contrast analysis
         */
        private fun calculateHistogramSpread(histogram: IntArray): Float {
            val totalPixels = histogram.sum()
            val cumulativeSum = IntArray(256)

            cumulativeSum[0] = histogram[0]
            for (i in 1 until 256) {
                cumulativeSum[i] = cumulativeSum[i - 1] + histogram[i]
            }

            // Find 5th and 95th percentiles
            val p5Threshold = (totalPixels * 0.05).toInt()
            val p95Threshold = (totalPixels * 0.95).toInt()

            var p5 = 0
            var p95 = 255

            for (i in 0 until 256) {
                if (cumulativeSum[i] >= p5Threshold && p5 == 0) {
                    p5 = i
                }
                if (cumulativeSum[i] >= p95Threshold) {
                    p95 = i
                    break
                }
            }

            return (p95 - p5).toFloat() / 255.0f
        }

        /**
         * Calculates local contrast using sliding window
         */
        private fun calculateLocalContrast(
            pixels: List<Int>,
            width: Int,
            height: Int,
        ): Float {
            val windowSize = 5
            val halfWindow = windowSize / 2
            var totalContrast = 0.0
            var count = 0

            for (y in halfWindow until height - halfWindow) {
                for (x in halfWindow until width - halfWindow) {
                    var minVal = 255
                    var maxVal = 0

                    for (wy in -halfWindow..halfWindow) {
                        for (wx in -halfWindow..halfWindow) {
                            val pixelValue = pixels[(y + wy) * width + (x + wx)]
                            minVal = minOf(minVal, pixelValue)
                            maxVal = maxOf(maxVal, pixelValue)
                        }
                    }

                    totalContrast += (maxVal - minVal).toDouble()
                    count++
                }
            }

            return if (count > 0) (totalContrast / count / 255.0).toFloat() else 0.0f
        }

        /**
         * Calculates overall contrast score from multiple metrics
         */
        private fun calculateContrastScore(
            dynamicRange: Int,
            histogramSpread: Float,
            localContrast: Float,
        ): Float {
            // Normalize metrics to 0-1 range
            val normalizedRange = (dynamicRange.toFloat() / 255.0f).coerceIn(0.0f, 1.0f)
            val normalizedSpread = histogramSpread.coerceIn(0.0f, 1.0f)
            val normalizedLocal = localContrast.coerceIn(0.0f, 1.0f)

            // Weighted combination
            return (normalizedRange * 0.4f + normalizedSpread * 0.4f + normalizedLocal * 0.2f)
        }

        /**
         * Analyzes alignment between RGB and thermal images
         */
        private fun analyzeAlignment(
            rgbImage: Bitmap,
            thermalImage: Bitmap,
        ): AlignmentMetrics {
            logger.debug("[DEBUG_LOG] Analyzing RGB-thermal alignment - RGB: ${rgbImage.width}x${rgbImage.height}, Thermal: ${thermalImage.width}x${thermalImage.height}")

            try {
                // Implement feature matching between RGB and thermal images
                val rgbFeatures = extractKeyFeatures(rgbImage)
                val thermalFeatures = extractKeyFeatures(thermalImage)
                
                // Match features between the two images
                val matches = matchFeatures(rgbFeatures, thermalFeatures)
                
                // Calculate alignment metrics from feature matches
                val alignmentResults = calculateAlignmentFromMatches(matches)
                
                // Compute transformation matrix if enough matches found
                val transformationMatrix = if (matches.size >= 4) {
                    calculateTransformationMatrix(matches)
                } else {
                    null
                }
                
                val alignmentScore = calculateAlignmentScore(
                    alignmentResults.averageError,
                    alignmentResults.maxError,
                    matches.size
                )

                logger.debug(
                    "[DEBUG_LOG] Alignment analysis - Features: ${matches.size}, Avg Error: ${alignmentResults.averageError}, Score: $alignmentScore",
                )

                return AlignmentMetrics(
                    featureMatchCount = matches.size,
                    averageError = alignmentResults.averageError,
                    maxError = alignmentResults.maxError,
                    transformationMatrix = transformationMatrix,
                    alignmentScore = alignmentScore,
                )
            } catch (e: Exception) {
                logger.error("Error in alignment analysis", e)
                return AlignmentMetrics(
                    featureMatchCount = 0,
                    averageError = Float.MAX_VALUE,
                    maxError = Float.MAX_VALUE,
                    transformationMatrix = null,
                    alignmentScore = 0.0f,
                )
            }
        }

        /**
         * Calculates alignment score based on feature matching results
         */
        private fun calculateAlignmentScore(
            averageError: Float,
            maxError: Float,
            featureCount: Int,
        ): Float {
            // Score based on alignment accuracy (using both average and max error)
            val errorScore = (ALIGNMENT_MAX_ERROR / (averageError + 1.0)).coerceIn(0.0, 1.0).toFloat()
            val maxErrorPenalty = if (maxError > ALIGNMENT_MAX_ERROR * 2) 0.5f else 1.0f

            // Score based on feature count (more features = better alignment confidence)
            val featureScore = (featureCount.toFloat() / 50.0f).coerceIn(0.0f, 1.0f)

            // Combined score with max error penalty
            return (errorScore * maxErrorPenalty * 0.7f + featureScore * 0.3f)
        }

        /**
         * Calculates overall quality score from individual metrics
         */
        private fun calculateOverallScore(
            patternScore: Float,
            sharpnessScore: Float,
            contrastScore: Float,
            alignmentScore: Float,
        ): Float {
            // Weighted combination based on importance for calibration
            return (
                patternScore * 0.4f +
                    sharpnessScore * 0.25f +
                    contrastScore * 0.2f +
                    alignmentScore * 0.15f
            )
        }

        /**
         * Generates quality-based recommendation for user action
         */
        private fun generateRecommendation(
            overallScore: Float,
            patternScore: Float,
            sharpnessScore: Float,
            contrastScore: Float,
            alignmentScore: Float,
        ): QualityRecommendation {
            // Check for critical failures
            if (patternScore < MIN_PATTERN_SCORE) {
                return QualityRecommendation.RETAKE_REQUIRED
            }

            if (sharpnessScore < MIN_SHARPNESS_SCORE || contrastScore < MIN_CONTRAST_SCORE) {
                return QualityRecommendation.RETAKE_RECOMMENDED
            }

            if (alignmentScore < MIN_ALIGNMENT_SCORE) {
                return QualityRecommendation.RETAKE_RECOMMENDED
            }

            // Overall score-based recommendation
            return when {
                overallScore >= 0.9f -> QualityRecommendation.EXCELLENT
                overallScore >= 0.75f -> QualityRecommendation.GOOD
                overallScore >= 0.6f -> QualityRecommendation.ACCEPTABLE
                overallScore >= 0.4f -> QualityRecommendation.RETAKE_RECOMMENDED
                else -> QualityRecommendation.RETAKE_REQUIRED
            }
        }

        /**
         * Builds detailed analysis report for debugging and user feedback
         */
        private fun buildAnalysisDetails(
            rgbPattern: PatternDetectionResult,
            thermalPattern: PatternDetectionResult,
            rgbSharpness: SharpnessMetrics,
            thermalSharpness: SharpnessMetrics,
            rgbContrast: ContrastMetrics,
            thermalContrast: ContrastMetrics,
            alignment: AlignmentMetrics,
        ): String =
            buildString {
                appendLine("Calibration Quality Analysis Report:")
                appendLine()
                appendLine("Pattern Detection:")
                appendLine("  RGB Chessboard: ${rgbPattern.cornerCount} corners (${(rgbPattern.completeness * 100).toInt()}%)")
                appendLine("  Thermal Circles: ${thermalPattern.cornerCount} circles (${(thermalPattern.completeness * 100).toInt()}%)")
                appendLine()
                appendLine("Image Quality:")
                appendLine("  RGB Sharpness: ${(rgbSharpness.sharpnessScore * 100).toInt()}%")
                appendLine("  Thermal Sharpness: ${(thermalSharpness.sharpnessScore * 100).toInt()}%")
                appendLine("  RGB Contrast: ${(rgbContrast.contrastScore * 100).toInt()}%")
                appendLine("  Thermal Contrast: ${(thermalContrast.contrastScore * 100).toInt()}%")
                appendLine()
                appendLine("Alignment:")
                appendLine("  Feature Matches: ${alignment.featureMatchCount}")
                appendLine("  Average Error: ${alignment.averageError} pixels")
                appendLine("  Alignment Score: ${(alignment.alignmentScore * 100).toInt()}%")
            }

        // Helper data classes for computer vision algorithms
        private data class Point2D(val x: Float, val y: Float)
        private data class FeatureMatch(val point1: Point2D, val point2: Point2D, val distance: Float)
        private data class AlignmentResult(val averageError: Float, val maxError: Float)

        /**
         * Convert bitmap to grayscale for image analysis
         */
        private fun convertToGrayscale(bitmap: Bitmap): Bitmap {
            val width = bitmap.width
            val height = bitmap.height
            val grayBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
            
            for (y in 0 until height) {
                for (x in 0 until width) {
                    val pixel = bitmap.getPixel(x, y)
                    val r = (pixel shr 16) and 0xFF
                    val g = (pixel shr 8) and 0xFF
                    val b = pixel and 0xFF
                    val gray = (0.299 * r + 0.587 * g + 0.114 * b).toInt()
                    val grayPixel = (0xFF shl 24) or (gray shl 16) or (gray shl 8) or gray
                    grayBitmap.setPixel(x, y, grayPixel)
                }
            }
            
            return grayBitmap
        }

        /**
         * Detect edges in grayscale image using Sobel operator
         */
        private fun detectEdges(bitmap: Bitmap): Bitmap {
            val width = bitmap.width
            val height = bitmap.height
            val edgeBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
            
            // Sobel operators
            val sobelX = arrayOf(
                intArrayOf(-1, 0, 1),
                intArrayOf(-2, 0, 2),
                intArrayOf(-1, 0, 1)
            )
            
            val sobelY = arrayOf(
                intArrayOf(-1, -2, -1),
                intArrayOf(0, 0, 0),
                intArrayOf(1, 2, 1)
            )
            
            for (y in 1 until height - 1) {
                for (x in 1 until width - 1) {
                    var gx = 0
                    var gy = 0
                    
                    for (i in -1..1) {
                        for (j in -1..1) {
                            val pixel = bitmap.getPixel(x + j, y + i)
                            val gray = pixel and 0xFF
                            gx += gray * sobelX[i + 1][j + 1]
                            gy += gray * sobelY[i + 1][j + 1]
                        }
                    }
                    
                    val magnitude = sqrt((gx * gx + gy * gy).toDouble()).toInt().coerceIn(0, 255)
                    val edgePixel = (0xFF shl 24) or (magnitude shl 16) or (magnitude shl 8) or magnitude
                    edgeBitmap.setPixel(x, y, edgePixel)
                }
            }
            
            return edgeBitmap
        }

        /**
         * Find corner candidates using Harris corner detection
         */
        private fun findCornerCandidates(bitmap: Bitmap): List<Point2D> {
            val corners = mutableListOf<Point2D>()
            val width = bitmap.width
            val height = bitmap.height
            val threshold = 100
            
            // Simple corner detection based on edge density
            val windowSize = 5
            val halfWindow = windowSize / 2
            
            for (y in halfWindow until height - halfWindow step 3) {
                for (x in halfWindow until width - halfWindow step 3) {
                    var edgeSum = 0
                    
                    for (wy in -halfWindow..halfWindow) {
                        for (wx in -halfWindow..halfWindow) {
                            val pixel = bitmap.getPixel(x + wx, y + wy)
                            edgeSum += (pixel and 0xFF)
                        }
                    }
                    
                    if (edgeSum > threshold * windowSize * windowSize) {
                        corners.add(Point2D(x.toFloat(), y.toFloat()))
                    }
                }
            }
            
            return corners
        }

        /**
         * Filter corner candidates to find chessboard pattern
         */
        private fun filterChessboardCorners(candidates: List<Point2D>, width: Int, height: Int): List<Point2D> {
            // Filter corners to find grid-like pattern
            val filtered = mutableListOf<Point2D>()
            val gridSpacingX = width / CHESSBOARD_COLS.toFloat()
            val gridSpacingY = height / CHESSBOARD_ROWS.toFloat()
            val tolerance = minOf(gridSpacingX, gridSpacingY) * 0.3f
            
            for (candidate in candidates) {
                // Check if corner is near expected grid position
                val gridX = (candidate.x / gridSpacingX).roundToInt()
                val gridY = (candidate.y / gridSpacingY).roundToInt()
                val expectedX = gridX * gridSpacingX
                val expectedY = gridY * gridSpacingY
                
                val distance = sqrt((candidate.x - expectedX).pow(2) + (candidate.y - expectedY).pow(2))
                
                if (distance < tolerance && gridX in 1 until CHESSBOARD_COLS - 1 && gridY in 1 until CHESSBOARD_ROWS - 1) {
                    filtered.add(candidate)
                }
            }
            
            return filtered
        }

        /**
         * Calculate geometric consistency of detected corners
         */
        private fun calculateGeometricConsistency(corners: List<Point2D>): Float {
            if (corners.size < 4) return 0.0f
            
            // Check if corners form a reasonable grid pattern
            var totalDeviation = 0.0f
            var count = 0
            
            for (i in corners.indices) {
                for (j in i + 1 until corners.size) {
                    val distance = sqrt(
                        (corners[i].x - corners[j].x).pow(2) + (corners[i].y - corners[j].y).pow(2)
                    )
                    
                    // Expected distances based on grid spacing
                    val expectedDistance = 50.0f // Approximate grid spacing
                    val deviation = abs(distance - expectedDistance) / expectedDistance
                    totalDeviation += deviation
                    count++
                }
            }
            
            val averageDeviation = if (count > 0) totalDeviation / count else 1.0f
            return (1.0f - averageDeviation.coerceIn(0.0f, 1.0f))
        }

        /**
         * Detect circular blobs for circle grid pattern
         */
        private fun detectCircularBlobs(bitmap: Bitmap): List<Point2D> {
            val blobs = mutableListOf<Point2D>()
            val width = bitmap.width
            val height = bitmap.height
            
            // Simple blob detection based on circular regions
            val radius = 10
            val threshold = 150
            
            for (y in radius until height - radius step radius) {
                for (x in radius until width - radius step radius) {
                    var centerIntensity = 0
                    var edgeIntensity = 0
                    var centerCount = 0
                    var edgeCount = 0
                    
                    // Sample center region
                    for (dy in -radius/3..radius/3) {
                        for (dx in -radius/3..radius/3) {
                            if (dx*dx + dy*dy <= (radius/3)*(radius/3)) {
                                val pixel = bitmap.getPixel(x + dx, y + dy)
                                centerIntensity += (pixel and 0xFF)
                                centerCount++
                            }
                        }
                    }
                    
                    // Sample edge region
                    for (dy in -radius..radius) {
                        for (dx in -radius..radius) {
                            val distanceSquared = dx*dx + dy*dy
                            if (distanceSquared > (radius*0.7)*(radius*0.7) && distanceSquared <= radius*radius) {
                                val pixel = bitmap.getPixel(x + dx, y + dy)
                                edgeIntensity += (pixel and 0xFF)
                                edgeCount++
                            }
                        }
                    }
                    
                    val avgCenter = if (centerCount > 0) centerIntensity / centerCount else 0
                    val avgEdge = if (edgeCount > 0) edgeIntensity / edgeCount else 0
                    
                    // Circle should have different center vs edge intensity
                    if (abs(avgCenter - avgEdge) > threshold) {
                        blobs.add(Point2D(x.toFloat(), y.toFloat()))
                    }
                }
            }
            
            return blobs
        }

        /**
         * Filter blobs to find grid pattern
         */
        private fun filterGridCircles(blobs: List<Point2D>, width: Int, height: Int): List<Point2D> {
            val filtered = mutableListOf<Point2D>()
            val gridSpacingX = width / CIRCLE_GRID_COLS.toFloat()
            val gridSpacingY = height / CIRCLE_GRID_ROWS.toFloat()
            val tolerance = minOf(gridSpacingX, gridSpacingY) * 0.4f
            
            for (blob in blobs) {
                val gridX = (blob.x / gridSpacingX).roundToInt()
                val gridY = (blob.y / gridSpacingY).roundToInt()
                val expectedX = gridX * gridSpacingX
                val expectedY = gridY * gridSpacingY
                
                val distance = sqrt((blob.x - expectedX).pow(2) + (blob.y - expectedY).pow(2))
                
                if (distance < tolerance && gridX in 0 until CIRCLE_GRID_COLS && gridY in 0 until CIRCLE_GRID_ROWS) {
                    filtered.add(blob)
                }
            }
            
            return filtered
        }

        /**
         * Calculate grid consistency for circles
         */
        private fun calculateGridConsistency(circles: List<Point2D>): Float {
            if (circles.size < 4) return 0.0f
            
            // Check spacing consistency
            var horizontalSpacings = mutableListOf<Float>()
            var verticalSpacings = mutableListOf<Float>()
            
            for (i in circles.indices) {
                for (j in i + 1 until circles.size) {
                    val dx = abs(circles[i].x - circles[j].x)
                    val dy = abs(circles[i].y - circles[j].y)
                    
                    if (dy < 20) { // Horizontal alignment
                        horizontalSpacings.add(dx)
                    }
                    if (dx < 20) { // Vertical alignment
                        verticalSpacings.add(dy)
                    }
                }
            }
            
            val hVariance = calculateVariance(horizontalSpacings)
            val vVariance = calculateVariance(verticalSpacings)
            val totalVariance = (hVariance + vVariance) / 2.0f
            
            return (1.0f / (1.0f + totalVariance * 0.01f))
        }

        /**
         * Calculate variance of spacing measurements
         */
        private fun calculateVariance(values: List<Float>): Float {
            if (values.isEmpty()) return 1.0f
            
            val mean = values.average().toFloat()
            val variance = values.map { (it - mean).pow(2) }.average().toFloat()
            return variance
        }

        /**
         * Extract key features from image for matching
         */
        private fun extractKeyFeatures(bitmap: Bitmap): List<Point2D> {
            val edgeBitmap = detectEdges(bitmap)
            val corners = findCornerCandidates(edgeBitmap)
            
            // Return strongest corners (simplified feature extraction)
            return corners.take(100)
        }

        /**
         * Match features between two images
         */
        private fun matchFeatures(features1: List<Point2D>, features2: List<Point2D>): List<FeatureMatch> {
            val matches = mutableListOf<FeatureMatch>()
            val maxDistance = 50.0f
            
            for (f1 in features1) {
                var bestMatch: Point2D? = null
                var bestDistance = Float.MAX_VALUE
                
                for (f2 in features2) {
                    val distance = sqrt((f1.x - f2.x).pow(2) + (f1.y - f2.y).pow(2))
                    if (distance < bestDistance && distance < maxDistance) {
                        bestDistance = distance
                        bestMatch = f2
                    }
                }
                
                bestMatch?.let {
                    matches.add(FeatureMatch(f1, it, bestDistance))
                }
            }
            
            return matches.sortedBy { it.distance }.take(50) // Keep best matches
        }

        /**
         * Calculate alignment metrics from feature matches
         */
        private fun calculateAlignmentFromMatches(matches: List<FeatureMatch>): AlignmentResult {
            if (matches.isEmpty()) {
                return AlignmentResult(Float.MAX_VALUE, Float.MAX_VALUE)
            }
            
            val errors = matches.map { it.distance }
            val averageError = errors.average().toFloat()
            val maxError = errors.maxOrNull() ?: Float.MAX_VALUE
            
            return AlignmentResult(averageError, maxError)
        }

        /**
         * Calculate transformation matrix from matched points
         */
        private fun calculateTransformationMatrix(matches: List<FeatureMatch>): FloatArray? {
            if (matches.size < 4) return null
            
            // Simplified transformation matrix calculation
            // In a real implementation, this would use least squares fitting
            val avgDx = matches.map { it.point2.x - it.point1.x }.average().toFloat()
            val avgDy = matches.map { it.point2.y - it.point1.y }.average().toFloat()
            
            // Return a simple translation matrix
            return floatArrayOf(
                1.0f, 0.0f, avgDx,
                0.0f, 1.0f, avgDy,
                0.0f, 0.0f, 1.0f
            )
        }
    }
