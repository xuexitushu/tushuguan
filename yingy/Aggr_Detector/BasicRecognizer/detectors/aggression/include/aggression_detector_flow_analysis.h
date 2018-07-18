//aggression_detector_flow_analysis.h
//
// Created by hy
//

#ifndef ICCTV_DETECTORS_AGGRESSION_DETECTOR_FLOW_ANALYSIS_H
#define ICCTV_DETECTORS_AGGRESSION_DETECTOR_FLOW_ANALYSIS_H


#include <aggression_detector_base.h>
#include <reader_aggression_detector.h>
#include <deque>

namespace icctv {

    struct Flow{
        int angle;
        double magnitude;
        void setA(int a){
            angle = a;
        }
        void setM(double m){
            magnitude = m;
        }
        int getA(){
            return angle;
        }

        double getM(){
            return magnitude;
        }
    };


    struct Group{
        std::deque<Flow> group;
        void setG(std::deque<Flow> g){
            group = g;
        }
        std::deque<Flow> getG(){
            return group;
        }

        int size(){
            return group.size();
        }
    };


    class AggressionDetectorFlowAnalysis : public AggressionDetectorBase {
    public:
        AggressionDetectorFlowAnalysis(const ReaderAggressionDetector& config,
                                 basicrecognizerapp::Speaker::Ptr speaker = NULL); //throws

        ~AggressionDetectorFlowAnalysis();

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

        Flow flow;
        std::deque<Flow> all_flows;
        std::deque<Group> main_angle_group;
        std::deque<Group> all_flow_groups;
        int dense_counter;
        int thresh_a1; //5
        int thresh_a2; //140
        float thresh_a3; //0.32


        cv::Size oflow_winsize;
        cv::Mat prev_gray_frame;
        cv::Mat opticalFlow;
        std::vector<cv::Point2f> points1;
        std::vector<cv::Point2f> points2;


        void removeNoise(std::vector<Flow> flows_vec);
        void getMainAngleGroup(std::deque<Flow> flows_vec);
        float calcSumMagnitudesM();
        float calcSumMagnitudesS();
        int countCross(cv::Mat opf_img);
        void setAggression(cv::Mat& img);

        void logAllParams();

    public:
        typedef std::shared_ptr<AggressionDetectorFlowAnalysis> Ptr;
    };
}

#endif //ICCTV_DETECTORS_AGGRESSION_DETECTOR_FLOW_ANALYSIS_H

