//aggression_detector.h
//
//

#ifndef ICCTV_RECOGNIZER_AGGRESSIONDETECTOR_H
#define ICCTV_RECOGNIZER_AGGRESSIONDETECTOR_H

#include <memory>
#include <opencv2/core/core.hpp>
#include <opencv2/video/tracking.hpp>
#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <Speaker.h>
#include <aggression_detector_base.h>
#include <reader_aggression_detector.h>

namespace icctv {
    class AggressionDetector : public AggressionDetectorBase {
    public:
        AggressionDetector(const ReaderAggressionDetector& config,
                           basicrecognizerapp::Speaker::Ptr speaker = NULL); //throws
        ~AggressionDetector();

        virtual bool detect(const cv::Mat& img, cv::Mat& output);

    private:
        bool need_to_init;
        bool hity;
        int aggrcounter;
        int timer;
        int max_points;
        int min_distance;
        int step_size;
        int haar_min_neighbors;
        int haar_min_window_size;
        int haar_max_window_size;
        int min_vector_size;
        int max_vector_size;
        float haar_scale_factor;
        float quality_level;
        std::string debug;
        cv::Size oflow_winsize;
        cv::Mat prev_gray_frame;
        std::vector<cv::Point2f> points1;
        std::vector<cv::Point2f> points2;
        std::vector<cv::Rect> hits;
        ReaderAggressionDetector config;

        cv::CascadeClassifier haar_cascade;

        bool loadClassifier(const char* path_to_cascade_classifier);
        void setDebugMode(std::string debug);
        void setMaxPoints(int points);
        void setOflowWinsize(int win_size);
        void setQualityLevel(float level);
        void setMinDistance(int min_distance);
        void setStepSize(int step_size);
        void setMinVectorSize(int min_vector_size);
        void setMaxVectorSize(int max_vector_size);
        void setHaarScaleFactor(float scale_factor);
        void setHaarMinNeighbours(int min_neighbours);
        void setHaarMinWindowsSize(int min_window_size);
        void setHaarMaxWindowsSize(int max_window_size);

        //Copy construction is not permitted
        AggressionDetector(const AggressionDetector& copy);

        AggressionDetector();

    public:
        typedef std::shared_ptr<AggressionDetector> Ptr;

    };
}

#endif //ICCTV_RECOGNIZER_AGGRESSIONDETECTOR_H

