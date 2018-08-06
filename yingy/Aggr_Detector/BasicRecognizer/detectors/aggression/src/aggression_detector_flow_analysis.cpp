//aggression_detector_flow_analysis.cpp
//

// Created by hy on 20.06.18.

//



#include "aggression_detector_flow_analysis.h"

#include <opencv2/imgproc.hpp>

#include <opencv2/video/tracking.hpp>

#include <opencv2/objdetect/objdetect.hpp>

#include <opencv2/highgui/highgui.hpp>

#include <deque>





icctv::AggressionDetectorFlowAnalysis::AggressionDetectorFlowAnalysis(const ReaderAggressionDetector& config,

                                                          basicrecognizerapp::Speaker::Ptr speaker)

        : split(10),

          history(3),//5

          aggression_duration_threshold(36),

          need_to_init(true),

          max_points(1000),

          min_distance(20),

          quality_level(0.005),

          target_width(800),

          target_height(600),

          left_b(0),

          right_b(800),

          upper_b(0),

          lower_b(600),

          oflow_winsize(cv::Size(25, 25)),

          min_vector_size(5),

          max_vector_size(40),

          dense_counter(2),

          thresh_a1(5),

          thresh_a2(140),

          thresh_a3(0.21)

{

    this->speaker = speaker;



    try {

        this->split = config.getSplit();

        this->history = config.getHistory();

        this->aggression_duration_threshold = config.getDuration();

        this->min_vector_size = config.getMinVecSize();

        this->max_vector_size = config.getMaxVecSize();

        this->oflow_winsize = cv::Size(config.getOflowWinsize(), config.getOflowWinsize());

        this->target_width = config.getPrepCropW();

        this->target_height = config.getPrepCropH();

        this->left_b = config.getLeftBoundary();

        this->right_b = config.getRightBoundary();

        this->upper_b = config.getUpperBoundary();

        this->lower_b = config.getLowerBoundary();



        this->dense_counter = config.getDenseCounter();

        this->thresh_a1 = config.getThreshA1();

        this->thresh_a2 = config.getThreshA2();

        this->thresh_a3 = config.getThreshA3();

        logAllParams();



        opticalFlow = cv::Mat(target_height, target_width, CV_8UC1, cv::Scalar(0));

    }

    catch (...) {

        throw std::runtime_error("Can't find/read config file!");

    }

}



icctv::AggressionDetectorFlowAnalysis::~AggressionDetectorFlowAnalysis() {

    //

}



bool icctv::AggressionDetectorFlowAnalysis::detect(const cv::Mat& img, cv::Mat& output) {

    cv::GaussianBlur(img, output, cv::Size(5, 5), 0.5, 0.5);

    cv::Mat grayFrames;

    cv::cvtColor(output, grayFrames, CV_BGR2GRAY);

    int framewidth = output.cols;

    int frameheight = output.rows;

    //opticalFlow(frameheight, framewidth, CV_8UC1, cv::Scalar(0));

    opticalFlow.setTo(cv::Scalar(0));



    int i,k;

    //Flow flow_obj;

    const double PI  =3.141592653589793238463;

    float sum_all = 0.001;

    float sum_main = 0.001;

    float p;

    int angle;

    int cross_num;

    all_flows.clear();

    all_flows.shrink_to_fit();







    std::vector<uchar> status;

    std::vector<float> err;



    cv::TermCriteria termcrit(CV_TERMCRIT_ITER | CV_TERMCRIT_EPS, 20, 0.03);



    if (need_to_init) {

        goodFeaturesToTrack(grayFrames,

                            points1,

                            max_points,

                            quality_level,

                            min_distance,

                            cv::Mat());



        need_to_init = false;

    } else if (!points2.empty()) {

        goodFeaturesToTrack(grayFrames,

                            points1,

                            max_points,

                            quality_level,

                            min_distance,

                            cv::Mat());



        cv::calcOpticalFlowPyrLK(prev_gray_frame,

                                 grayFrames,

                                 points2,

                                 points1,

                                 status,

                                 err,

                                 oflow_winsize,

                                 3,

                                 termcrit,

                                 0,

                                 0.001);



        for (i = k = 0; i < points2.size(); i++) {

            double res = cv::norm(points1[i] - points2[i]);

            if ((points1[i].x - points2[i].x) != 0 and res > this->min_vector_size and res < this->max_vector_size) {

                line(opticalFlow, points1[i], points2[i], cv::Scalar(255), 1, 1, 0);

                line(output, points1[i], points2[i], cv::Scalar(0, 0, 255), 1, 1, 0);

                //add flow elements

                angle = int(atan2(points1[i].y - points2[i].y, points1[i].x - points2[i].x) * 180 / PI);

                flow.setA(angle);

                flow.setM(res);

                all_flows.push_back(flow);

            }

            /*else {

                if (res > this->min_vector_size and res < this->max_vector_size) {

                    line(opticalFlow, points1[i], points2[i], cv::Scalar(255), 1, 1, 0);

                    line(output, points1[i], points2[i], cv::Scalar(0, 0, 255), 1, 1, 0);

                    //add flow elements

                    angle = int(atan2(points1[i].y - points2[i].y, points1[i].x - points2[i].x) * 180 / PI);

                    flow.setA(angle);

                    flow.setM(res);

                    all_flows.push_back(flow);



                }

            }*/

            points1[k++] = points1[i];

        }

        goodFeaturesToTrack(grayFrames,

                            points1,

                            max_points,

                            quality_level,

                            min_distance,

                            cv::Mat());

    }





    p = 1;

    getMainAngleGroup(all_flows);

    sum_all = calcSumMagnitudesS();

    sum_main = calcSumMagnitudesM();

    p = sum_main/sum_all;

    cross_num = countCross(opticalFlow);//opticalFlow



    auto detectionresult = false;



    if (sum_main > thresh_a2 && p < thresh_a3){

        detectionresult = true;

    }

    speaker->log_debug(std::to_string(sum_main) + " - " + std::to_string(sum_all) + " - " + std::to_string(p) + " - " + std::to_string(cross_num)); //hy

    //speaker->log_debug(std::to_string(opticalFlow.cols) + " - " + std::to_string(opticalFlow.rows) + " - " + std::to_string(opticalFlow.type())); //hy



    swap(points2, points1);

    points1.clear();

    grayFrames.copyTo(prev_gray_frame);



    return detectionresult;

}





int icctv::AggressionDetectorFlowAnalysis::countCross(cv::Mat opf_img_gray){

    int thresh_value = 255;

    int cross_count = 0;

    int framewidth = opf_img_gray.cols;

    int frameheight = opf_img_gray.rows;

    int k=0;

    cv::Mat opf_bin;

    cv::threshold(opf_img_gray, opf_bin, 10, 255, cv::THRESH_BINARY);

    //threshold( src_gray, dst, threshold_value, max_binary_value, threshold_type );

    for(int i = 0; i < framewidth-1; i++){

        for (int j = 0; j < frameheight-1; j++){

            k = 0;

            if((opf_bin.at<int>(i,j) + opf_bin.at<int>(i,j)) > thresh_value){

                if(opf_bin.at<int>(i-1,j-1) == thresh_value)

                    k++;

                if(opf_bin.at<int>(i,j-1) == thresh_value)

                    k++;

                if(opf_bin.at<int>(i+1,j-1) == thresh_value)

                    k++;

                if(opf_bin.at<int>(i+1,j+1) == thresh_value)

                    k++;

                if(opf_bin.at<int>(i,j+1) == thresh_value)

                    k++;

                if(opf_bin.at<int>(i-1,j+1) == thresh_value)

                    k++;

                if(k > 3){

                    cross_count++;

                }

            }

        }

    }

    return cross_count;

}





void icctv::AggressionDetectorFlowAnalysis::getMainAngleGroup(std::deque<Flow> all_flow_elements){

    int max_num_of_angles = 0;

    std::deque<Flow> tmp_list;

    Group group;

    Group max_group;

    std::deque<Group> groups;

    std::deque<Group> group_of_max;



    auto group_total = 12;

    auto group_unit = 360/group_total;



    for(int n = 0; n < group_total; n++){

        tmp_list.clear();

        tmp_list.shrink_to_fit();

        for(auto & element:all_flow_elements) {

            if (element.getA() < 0)

                element.setA(360 + element.getA());

            if (element.getA() > n * group_unit && element.getA() < (n + 1) * group_unit) {

                tmp_list.push_back(element);

                all_flow_elements.pop_front();

            }

        }

        group.setG(tmp_list);

        groups.push_back(group);



    }

    all_flow_groups = groups;



    for(auto & g:this->all_flow_groups){

        if (g.size() > max_num_of_angles){

            max_num_of_angles = g.size();

            max_group.setG(g.getG());

        }

    }

    group_of_max.push_back(max_group);

    main_angle_group = group_of_max;



}





float icctv::AggressionDetectorFlowAnalysis::calcSumMagnitudesM(){

    float sum_all = 0;

    Group grp;

    for(auto & g:this->main_angle_group){

        for(auto & f:g.getG()){

            sum_all += f.getM();

        }

    }

    return sum_all;

}



float icctv::AggressionDetectorFlowAnalysis::calcSumMagnitudesS(){

    float sum_all = 0;

    Group grp;

    for(auto & g:this->all_flow_groups){

        for(auto & f:g.getG()){

            sum_all += f.getM();

        }

    }



    return sum_all;

}





void icctv::AggressionDetectorFlowAnalysis::setAggression(cv::Mat& img) {

    std::vector<cv::Mat> channels(3);

    cv::split(img, channels);

    auto font_channel = 1;

    cv::Rect roi = cv::Rect(40, 40, 60, 30);

    //cv::Rect roi = cv::Rect(b.left, b.top, b.w, b.h);



    cv::putText(channels[font_channel],

                std::to_string(dense_counter*50),

                cv::Point(40,100),

                cv::FONT_HERSHEY_SIMPLEX,

                0.5,

                cv::Scalar(255),

                1

    );



    channels[0](roi).setTo(this->dense_counter / 255);



    cv::merge(channels, img);

}





bool icctv::AggressionDetectorFlowAnalysis::hasPreprocessingStep() {

    return true;

}



void icctv::AggressionDetectorFlowAnalysis::logAllParams() {

    this->speaker->log_info("~~~~~");

    this->speaker->log_info("max points: " + std::to_string(max_points));

    this->speaker->log_info("min_distance: " + std::to_string(min_distance));

    this->speaker->log_info("min_vector_size: " + std::to_string(min_vector_size));

    this->speaker->log_info("max_vector_size: " + std::to_string(max_vector_size));

    this->speaker->log_info("split: " + std::to_string(split));

    this->speaker->log_info("history: " + std::to_string(history));

    this->speaker->log_info("aggression_duration_threshold: " + std::to_string(aggression_duration_threshold));

    this->speaker->log_info("left_b: " + std::to_string(left_b));

    this->speaker->log_info("right_b: " + std::to_string(right_b));

    this->speaker->log_info("upper_b: " + std::to_string(upper_b));

    this->speaker->log_info("lower_b: " + std::to_string(lower_b));

    this->speaker->log_info("dense_counter: " + std::to_string(dense_counter));

    this->speaker->log_info("thresh_a1: " + std::to_string(thresh_a1));

    this->speaker->log_info("thresh_a2: " + std::to_string(thresh_a2));

    this->speaker->log_info("thresh_a3: " + std::to_string(thresh_a3));

    this->speaker->log_info("~~~~~");

}

