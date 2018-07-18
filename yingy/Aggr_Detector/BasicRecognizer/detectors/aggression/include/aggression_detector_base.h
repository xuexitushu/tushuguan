//aggression_detector_base.h
//
//

#ifndef ICCTV_RECOGNIZER_AGGRESSION_DETECTOR_BASE_H
#define ICCTV_RECOGNIZER_AGGRESSION_DETECTOR_BASE_H

#include <memory>

#include <opencv2/core.hpp>

#include <Speaker.h>

namespace icctv {
    class AggressionDetectorBase {
    public:
        virtual bool detect(const cv::Mat &img, cv::Mat &output) = 0;
        virtual bool hasPreprocessingStep(){return true;}

    protected:
        basicrecognizerapp::Speaker::Ptr speaker;

    public:
        typedef std::shared_ptr<AggressionDetectorBase> Ptr;
    };
}

#endif //ICCTV_RECOGNIZER_AGGRESSION_DETECTOR_BASE_H

