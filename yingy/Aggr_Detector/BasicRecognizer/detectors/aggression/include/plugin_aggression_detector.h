//plugin_aggression_detector.h
//

#ifndef ICCTV_RECOGNIZER_PLUGIN_AGGRESSION_DETECTOR_H

#define ICCTV_RECOGNIZER_PLUGIN_AGGRESSION_DETECTOR_H



#include <string>

#include <mutex>

#include <unistd.h>



#include <boost/thread/thread.hpp>



#include <opencv2/core/core.hpp>

#include <opencv2/video/tracking.hpp>

#include <opencv2/objdetect/objdetect.hpp>

#include <opencv2/highgui/highgui.hpp>



#include <TaskRunner.h>

#include <fps_counter.h>

//#include <aggression_detector.h>

#include <aggression_detector_base.h>



#include <detector_status_aggression.h>

#include <reader_aggression_detector.h>



namespace basicrecognizerapp {



    class PluginAggressionDetector : public Plugin {

    public:



        PluginAggressionDetector();



        ~PluginAggressionDetector();



        void Thread();



        void stop();



        std::string getStatus();



        DetectorStatus::Ptr getDetectorStatus();



        void setFrameToStopOn(int frame);



        void setMaximalPoints(int max_points);



        bool getThreadStatus();



        void onEvent(EventType event);



        int myMain(std::vector<std::string> cams, std::string detectorcfg);



    private:

        bool ready;

        bool audio_signal;

        bool is_thread_running;

        bool is_audio_enabled;

        bool is_verbose;

        bool has_preprocessing_step;



        int performance;

        std::string conn;

        std::string detectorcfg;

        std::string debug;

        FPSCounter fps;

        boost::thread *thrdx;

        int frame_to_stop;

        int maximal_points;

        int prep_crop_h;

        int prep_crop_w;

        int detection_interval;

        float prep_scale;



        icctv::AggressionDetectorBase::Ptr detector;

        DetectorStatus::Ptr status;



        ReaderAggressionDetector config;



        bool initDetector(const ReaderAggressionDetector& config);

        void preprocessImg(const cv::Mat image, cv::Mat& processed_img);

    };



}



#endif //ICCTV_RECOGNIZER_PLUGIN_AGGRESSION_DETECTOR_H

