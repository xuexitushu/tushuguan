//aggression_detector_motion.h
//
//

#ifndef ICCTV_RECOGNIZER_AGGRESSION_DETECTOR_MOTION_H
#define ICCTV_RECOGNIZER_AGGRESSION_DETECTOR_MOTION_H

#include <aggression_detector_base.h>
#include <reader_aggression_detector.h>

namespace icctv {

    struct Bin{
        int top;
        int left;
        int w;
        int h;
        int level;
        int counter;
    };

    class AggressionDetectorMotion : public AggressionDetectorBase {
    public:
        AggressionDetectorMotion(const ReaderAggressionDetector& config,
                                 basicrecognizerapp::Speaker::Ptr speaker = NULL); //throws

        ~AggressionDetectorMotion();

        virtual bool detect(const cv::Mat& img, cv::Mat& output);
        virtual bool hasPreprocessingStep();

    private:
        bool need_to_init;
        int split;
        int history;
        int max_agression_level;
        int cooldown_rate;
        int aggression_duration_threshold;
        int min_vector_size;
        int max_vector_size;
        int max_points;
        int min_distance;
        float quality_level;
        float counter_threshold;

        int target_width;
        int target_height;
        int left_b;
        int right_b;
        int upper_b;
        int lower_b;

        cv::Size oflow_winsize;
        cv::Mat prev_gray_frame;
        cv::Mat opticalFlow;
        std::vector<cv::Point2f> points1;
        std::vector<cv::Point2f> points2;
        std::vector<Bin> bins;

        void createBinList(int w, int h, int split_x, int split_y);
        void updateBinsWithFlow(int max_level = 1000);
        bool markAggressionBinOnImage(cv::Mat& img);
        void coolDownBins();
        void updateBinCounter();
        void logAllParams();

    public:
        typedef std::shared_ptr<AggressionDetectorMotion> Ptr;
    };
}

#endif //ICCTV_RECOGNIZER_AGGRESSION_DETECTOR_MOTION_H

