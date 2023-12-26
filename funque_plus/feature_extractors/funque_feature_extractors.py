from typing import Dict, Any, Optional

from videolib import Video, standards
from qualitylib.feature_extractor import FeatureExtractor
from qualitylib.result import Result

import numpy as np
import cv2
import pandas as pd
import sys
import time
from ..features.funque_atoms import pyr_features, vif_utils, filter_utils


class FunqueFeatureExtractor(FeatureExtractor):
    '''
    A feature extractor that implements FUNQUE.
    '''
    NAME = 'FUNQUE_fex'
    VERSION = '1.0'
    res_names = ['Frame','FUNQUE_feature_vif_scale0_score','FUNQUE_feature_vif_scale1_score','FUNQUE_feature_adm_scale0_score',
                 'FUNQUE_feature_ssim_mean_scale0_score','FUNQUE_feature_ssim_cov_scale0_score','FUNQUE_feature_mad_scale0_score'
                ]
    prof_feat =['Frame','time_taken','resizer','filters','dwt','ssim','vif','adm','mad']  
    
    def __init__(self, use_cache: bool = True, sample_rate: Optional[int] = None) -> None:
        super().__init__(use_cache, sample_rate)
        self.wavelet_levels = 1
        self.vif_extra_levels = 1
        self.csf = 'ngan_spat'
        self.wavelet = 'haar'
        self.feat_names = \
            [f'vif_approx_scalar_channel_y_scale_{scale+1}' for scale in range(self.wavelet_levels+self.vif_extra_levels)] + \
            [f'ssim_cov_channel_y_levels_{self.wavelet_levels}', f'dlm_channel_y_scale_{self.wavelet_levels}', f'motion_channel_y_scale_{self.wavelet_levels}'] 
            

    def _run_on_asset(self, asset_dict: Dict[str, Any]) -> Result:
        sample_interval = self._get_sample_interval(asset_dict)
        feats_dict = {key: [] for key in self.feat_names}
        res_dict = {key: [] for key in self.res_names}
        prof_dict = {key: [] for key in self.prof_feat}

        channel_names = ['y', 'u', 'v']
        channel_name = 'y'
        channel_ind = 0
        
        if self.wavelet_levels:
            levels = 0
            
        with Video(
            asset_dict['ref_path'], mode='r',
            standard=asset_dict['ref_standard'],
            width=asset_dict['width'], height=asset_dict['height']
        ) as v_ref:
            with Video(
                asset_dict['dis_path'], mode='r',
                standard=asset_dict['dis_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_dis:
                # w_crop = (v_ref.width >> (self.wavelet_levels+self.vif_extra_levels+1)) << (self.wavelet_levels+self.vif_extra_levels)
                # h_crop = (v_ref.height >> (self.wavelet_levels+self.vif_extra_levels+1)) << (self.wavelet_levels+self.vif_extra_levels)

                w_pad = (((v_ref.width//2) + 2**(self.wavelet_levels+self.vif_extra_levels)-1) >> (self.wavelet_levels+self.vif_extra_levels)) << (self.wavelet_levels+self.vif_extra_levels)
                h_pad = (((v_ref.height//2) + 2**(self.wavelet_levels+self.vif_extra_levels)-1) >> (self.wavelet_levels+self.vif_extra_levels)) << (self.wavelet_levels+self.vif_extra_levels)

                for frame_ind, (frame_ref, frame_dis) in enumerate(zip(v_ref, v_dis)):
                    start_time = time.time()
                    res_dict['Frame'].append(frame_ind)
                    prof_dict['Frame'].append(frame_ind)
                    
                    resizer_start_time =time.time()
                    y_ref = cv2.resize(frame_ref.yuv[..., 0].astype(v_ref.standard.dtype), (frame_ref.width//2, frame_ref.height//2), interpolation=cv2.INTER_CUBIC).astype('float64')/asset_dict['ref_standard'].range
                    y_dis = cv2.resize(frame_dis.yuv[..., 0].astype(v_dis.standard.dtype), (frame_dis.width//2, frame_dis.height//2), interpolation=cv2.INTER_CUBIC).astype('float64')/asset_dict['dis_standard'].range
                    resizer_end_time = time.time()                 
                    # # Cropping to a power of 2 to avoid problems in WD-SSIM
                    # y_ref = y_ref[:h_crop, :w_crop]
                    # y_dis = y_dis[:h_crop, :w_crop]

                    # Padding to a power of 2 to avoid problems in SSIM
                    h_pad_amt = h_pad - y_ref.shape[0]
                    w_pad_amt = w_pad - y_ref.shape[1]
                    y_ref = np.pad(y_ref, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                    y_dis = np.pad(y_dis, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')

                    channel_ref = y_ref
                    channel_dis = y_dis
                                      
                    filters_start_time = time.time()
                    [channel_ref, channel_dis] = [filter_utils.filter_img(channel, self.csf, self.wavelet, channel=channel_ind) for channel in (channel_ref, channel_dis)]
                    dwt_start_time = filters_end_time = time.time()
                    [vif_pyr_ref, vif_pyr_dis] = [pyr_features.custom_wavedec2(channel, self.wavelet, 'periodization', self.wavelet_levels+self.vif_extra_levels) for channel in (channel_ref, channel_dis)]
                    dwt_end_time = time.time()
                    
                    pyr_ref = tuple([p[:1] for p in vif_pyr_ref])
                    pyr_dis = tuple([p[:1] for p in vif_pyr_dis])

                    if frame_ind % sample_interval:
                        prev_pyr_ref = pyr_ref.copy()
                        continue

                    # SSIM features
                    ssim_start_time = time.time()
                    ssim_mean_scales, ssim_cov_scales = pyr_features.ssim_pyr(pyr_ref, pyr_dis, pool='all')
                    ssim_end_time = time.time()
                    feats_dict[f'ssim_cov_channel_{channel_name}_levels_1'].append(ssim_cov_scales)
                    res_dict[f'FUNQUE_feature_ssim_mean_scale{levels}_score'].append(ssim_mean_scales)
                    res_dict[f'FUNQUE_feature_ssim_cov_scale{levels}_score'].append(ssim_cov_scales)        

                    # Scalar VIF features
                    vif_start_time = time.time()
                    vif_approx_scales = [vif_utils.vif_spatial(approx_ref, approx_dis, sigma_nsq=5, k=9, full=False) for approx_ref, approx_dis in zip(vif_pyr_ref[0], vif_pyr_dis[0])]
                    vif_end_time = time.time()
                    for lev, vif_approx_scale in enumerate(vif_approx_scales):
                        feats_dict[f'vif_approx_scalar_channel_{channel_name}_scale_{lev+1}'].append(vif_approx_scale)
                        res_dict[f'FUNQUE_feature_vif_scale{lev}_score'].append(vif_approx_scale)
                        
                    # DLM features
                    dlm_start_time = time.time()
                    dlm_val = pyr_features.dlm_pyr(pyr_ref, pyr_dis, csf=None)
                    dlm_end_time = time.time()
                    feats_dict[f'dlm_channel_{channel_name}_scale_1'].append(dlm_val)
                    res_dict[f'FUNQUE_feature_adm_scale{levels}_score'].append(dlm_val)
                    
                    # MAD features
                    mad_start_time = time.time()
                    if frame_ind != 0:
                        subband = pyr_ref[0][0]
                        prev_subband = prev_pyr_ref[0][0]
                        motion_val = np.mean(np.abs(subband - prev_subband))
                    else:
                        motion_val = 0
                    mad_end_time = time.time()
                    feats_dict[f'motion_channel_{channel_name}_scale_1'].append(motion_val)
                    res_dict[f'FUNQUE_feature_mad_scale{levels}_score'].append(motion_val)
                    
                    prev_pyr_ref = pyr_ref
                    end_time = time.time()
                    prof_dict['time_taken'].append(end_time - start_time)
                    prof_dict['resizer'].append(resizer_end_time - resizer_start_time)
                    prof_dict['filters'].append(filters_end_time - filters_start_time)
                    prof_dict['dwt'].append(dwt_end_time - dwt_start_time)
                    prof_dict['ssim'].append(ssim_end_time - ssim_start_time)
                    prof_dict['vif'].append(vif_end_time - vif_start_time)
                    prof_dict['adm'].append(dlm_end_time - dlm_start_time)
                    prof_dict['mad'].append(mad_end_time - mad_start_time)
                 
        prof_data = {k: pd.Series(v + ['Sum'] if k == 'Frame' else v + [sum(map(float, v))]) for k, v in prof_dict.items()}
        prof_df = pd.DataFrame(prof_data)
        prof_df.to_csv(asset_dict['profile_file'], index=False)
          
        data = {k: pd.Series(v) for k, v in res_dict.items()}
        res_df = pd.DataFrame(data)
        res_df.to_csv(asset_dict['out_file'], index=False)
        
        feats = np.array(list(feats_dict.values())).T
        print(f'Processed {asset_dict["dis_path"]}')
        return self._to_result(asset_dict, feats, list(feats_dict.keys()))


class YFunquePlusFeatureExtractor(FeatureExtractor):
    '''
    A feature extractor that implements Y-FUNQUE+.
    '''
    NAME = 'Y_FUNQUE_Plus_fex'
    VERSION = '1.0'
    res_names = ['Frame','FUNQUE_feature_adm_scale0_score', 
                 'FUNQUE_feature_ms_ssim_mean_scale0_score','FUNQUE_feature_ms_ssim_cov_scale0_score','FUNQUE_feature_ms_ssim_mink3_scale0_score','FUNQUE_feature_strred_scale0_score',
                 'FUNQUE_feature_ms_ssim_mean_scale1_score','FUNQUE_feature_ms_ssim_cov_scale1_score','FUNQUE_feature_ms_ssim_mink3_scale1_score','FUNQUE_feature_strred_scale1_score',
                 'FUNQUE_feature_ms_ssim_mean_scale2_score','FUNQUE_feature_ms_ssim_cov_scale2_score','FUNQUE_feature_ms_ssim_mink3_scale2_score','FUNQUE_feature_strred_scale2_score',
                 'FUNQUE_feature_ms_ssim_mean_scale3_score','FUNQUE_feature_ms_ssim_cov_scale3_score','FUNQUE_feature_ms_ssim_mink3_scale3_score','FUNQUE_feature_strred_scale3_score',
                ]
    prof_feat =['Frame','time_taken','resizer','filters','dwt','adm','ms_ssim','strred']
    
    def __init__(self, use_cache: bool = True, sample_rate: Optional[int] = None) -> None:
        super().__init__(use_cache, sample_rate)
        self.wavelet_levels = 4
        self.csf = 'nadenau_weight'
        self.wavelet = 'haar'
        self.feat_names = [f'ms_ssim_cov_channel_y_levels_{self.wavelet_levels}', f'dlm_channel_y_scale_{self.wavelet_levels}', f'strred_scalar_channel_y_levels_{self.wavelet_levels}', f'mad_ref_channel_y_scale_{self.wavelet_levels}']

    def _run_on_asset(self, asset_dict: Dict[str, Any]) -> Result:
        sample_interval = self._get_sample_interval(asset_dict)
        feats_dict = {key: [] for key in self.feat_names}
        res_dict = {key: [] for key in self.res_names}
        prof_dict = {key: [] for key in self.prof_feat}
        
        channel_names = ['y', 'u', 'v']
        channel_name = 'y'
        channel_ind = 0

        if self.wavelet_levels:
            levels = [0, 1, 2, 3]

        with Video(
            asset_dict['ref_path'], mode='r',
            standard=asset_dict['ref_standard'],
            width=asset_dict['width'], height=asset_dict['height']
        ) as v_ref:
            with Video(
                asset_dict['dis_path'], mode='r',
                standard=asset_dict['dis_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_dis:
                # w_crop = (v_ref.width >> (self.wavelet_levels+1)) << self.wavelet_levels
                # h_crop = (v_ref.height >> (self.wavelet_levels+1)) << self.wavelet_levels

                w_pad = (((v_ref.width//2) + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels
                h_pad = (((v_ref.height//2) + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels

                for frame_ind, (frame_ref, frame_dis) in enumerate(zip(v_ref, v_dis)):
                    start_time = time.time()
                    res_dict['Frame'].append(frame_ind)
                    prof_dict['Frame'].append(frame_ind)
                    
                    resizer_start_time =time.time()
                    y_ref = cv2.resize(frame_ref.yuv[..., 0].astype(v_ref.standard.dtype), (frame_ref.width//2, frame_ref.height//2), interpolation=cv2.INTER_CUBIC).astype('float64') / asset_dict['ref_standard'].range
                    y_dis = cv2.resize(frame_dis.yuv[..., 0].astype(v_dis.standard.dtype), (frame_dis.width//2, frame_dis.height//2), interpolation=cv2.INTER_CUBIC).astype('float64') / asset_dict['dis_standard'].range
                    resizer_end_time = time.time()
                    
                    # # Cropping to a power of 2 to avoid problems in SSIM
                    # y_ref = y_ref[:h_crop, :w_crop]
                    # y_dis = y_dis[:h_crop, :w_crop]

                    # Padding to a power of 2 to avoid problems in SSIM
                    h_pad_amt = h_pad - y_ref.shape[0]
                    w_pad_amt = w_pad - y_ref.shape[1]
                    y_ref = np.pad(y_ref, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                    y_dis = np.pad(y_dis, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                    #print(y_ref.shape, y_dis.shape, v_ref.width, v_ref.height, self.wavelet_levels)

                    channel_ref = y_ref
                    channel_dis = y_dis
                                       
                    dwt_start_time = time.time()
                    [pyr_ref, pyr_dis] = [pyr_features.custom_wavedec2(channel, self.wavelet, 'periodization', self.wavelet_levels) for channel in (channel_ref, channel_dis)]
                    dwt_end_time = filters_start_time = time.time()
                    [pyr_ref, pyr_dis] = [filter_utils.filter_pyr(pyr, self.csf, channel=channel_ind) for pyr in (pyr_ref, pyr_dis)]
                    filters_end_time = time.time()
                    
                    if frame_ind % sample_interval:
                        prev_pyr_ref = pyr_ref.copy()
                        prev_pyr_dis = pyr_dis.copy()
                        continue

                    # SSIM features
                    ms_ssim_start_time = time.time()
                    (ms_ssim_mean_scales, _), (ms_ssim_cov_scales, _), (ms_ssim_mink3_scales, _) = pyr_features.ms_ssim_pyr(pyr_ref, pyr_dis, pool='all')
                    ms_ssim_end_time = time.time()
                    feats_dict[f'ms_ssim_cov_channel_{channel_name}_levels_{self.wavelet_levels}'].append(ms_ssim_cov_scales[-1])
                    for level, mean, cov, mink in zip(levels, ms_ssim_mean_scales, ms_ssim_cov_scales, ms_ssim_mink3_scales):
                        res_dict[f'FUNQUE_feature_ms_ssim_mean_scale{level}_score'].append(mean)
                        res_dict[f'FUNQUE_feature_ms_ssim_cov_scale{level}_score'].append(cov)
                        res_dict[f'FUNQUE_feature_ms_ssim_mink3_scale{level}_score'].append(mink)

                    # DLM features
                    dlm_start_time = time.time()
                    dlm_val, dlm_level_wise_scores = pyr_features.dlm_pyr((None, [pyr_ref[1][-1]]), (None, [pyr_dis[1][-1]]), csf=None)
                    dlm_end_time = time.time()
                    feats_dict[f'dlm_channel_{channel_name}_scale_{self.wavelet_levels}'].append(dlm_val)
                    res_dict[f'FUNQUE_feature_adm_scale0_score'].append(dlm_val)

                    # MAD features
                    strred_start_time = time.time()
                    if frame_ind != 0:
                        #motion_val = np.mean(np.abs(pyr_ref[0][-1]- prev_pyr_ref[0][-1]))
                        # STRRED features
                        (_, _, strred_scales) = pyr_features.strred_hv_pyr(pyr_ref, pyr_dis, prev_pyr_ref, prev_pyr_dis, block_size=1)
                    else:
                        motion_val = 0
                        strred_scales = [0]*self.wavelet_levels
                    strred_end_time = time.time()
                    feats_dict[f'mad_ref_channel_{channel_name}_scale_{self.wavelet_levels}'].append(motion_val)

                    feats_dict[f'strred_scalar_channel_{channel_name}_levels_{self.wavelet_levels}'].append(strred_scales[-1])
                    for level, value in zip(levels, strred_scales):
                        res_dict[f'FUNQUE_feature_strred_scale{level}_score'].append(value) 

                    prev_pyr_ref = pyr_ref
                    prev_pyr_dis = pyr_dis
                    
                    end_time = time.time()
                    prof_dict['time_taken'].append(end_time - start_time)
                    prof_dict['resizer'].append(resizer_end_time - resizer_start_time)
                    prof_dict['filters'].append(filters_end_time - filters_start_time)
                    prof_dict['dwt'].append(dwt_end_time - dwt_start_time)
                    prof_dict['adm'].append(dlm_end_time - dlm_start_time)
                    prof_dict['ms_ssim'].append(ms_ssim_end_time - ms_ssim_start_time)
                    prof_dict['strred'].append(strred_end_time - strred_start_time)
                 
        prof_data = {k: pd.Series(v + ['Sum'] if k == 'Frame' else v + [sum(map(float, v))]) for k, v in prof_dict.items()}
        prof_df = pd.DataFrame(prof_data)
        prof_df.to_csv(asset_dict['profile_file'], index=False)
        
        data = {k: pd.Series(v) for k, v in res_dict.items()}
        res_df = pd.DataFrame(data)
        res_df.to_csv(asset_dict['out_file'], index=False)

        feats = np.array(list(feats_dict.values())).T

        print(f'Processed {asset_dict["dis_path"]}')
        return self._to_result(asset_dict, feats, list(feats_dict.keys()))


class FullScaleYFunquePlusFeatureExtractor(FeatureExtractor):
    '''
    A feature extractor that implements FS-Y-FUNQUE+.
    '''
    NAME = 'FS_Y_FUNQUE_Plus_fex'
    VERSION = '1.0'
    res_names = ['Frame','FUNQUE_feature_adm_scale0_score', 
                 'FUNQUE_feature_ms_ssim_mean_scale0_score','FUNQUE_feature_ms_ssim_cov_scale0_score','FUNQUE_feature_ms_ssim_mink3_scale0_score','FUNQUE_feature_strred_scale0_score',
                 'FUNQUE_feature_ms_ssim_mean_scale1_score','FUNQUE_feature_ms_ssim_cov_scale1_score','FUNQUE_feature_ms_ssim_mink3_scale1_score','FUNQUE_feature_strred_scale1_score',
                 'FUNQUE_feature_ms_ssim_mean_scale2_score','FUNQUE_feature_ms_ssim_cov_scale2_score','FUNQUE_feature_ms_ssim_mink3_scale2_score','FUNQUE_feature_strred_scale2_score',
                 'FUNQUE_feature_ms_ssim_mean_scale3_score','FUNQUE_feature_ms_ssim_cov_scale3_score','FUNQUE_feature_ms_ssim_mink3_scale3_score','FUNQUE_feature_strred_scale3_score',
                ]
    prof_feat =['Frame','time_taken','resizer','filters','dwt','adm','ms_ssim','strred']

    def __init__(self, use_cache: bool = True, sample_rate: Optional[int] = None) -> None:
        super().__init__(use_cache, sample_rate)
        self.wavelet_levels = 4
        self.csf = 'nadenau_spat'
        self.wavelet = 'haar'
        self.feat_names = [f'ms_ssim_cov_channel_y_levels_{self.wavelet_levels}', f'dlm_channel_y_scale_{self.wavelet_levels}', f'strred_scalar_channel_y_levels_{self.wavelet_levels}',
                           f'mad_dis_channel_y_scale_{self.wavelet_levels}']

    def _run_on_asset(self, asset_dict: Dict[str, Any]) -> Result:
        sample_interval = self._get_sample_interval(asset_dict)
        feats_dict = {key: [] for key in self.feat_names}
        res_dict = {key: [] for key in self.res_names}
        prof_dict = {key: [] for key in self.prof_feat}

        channel_names = ['y', 'u', 'v']
        channel_name = 'y'
        channel_ind = 0

        if self.wavelet_levels:
            levels = [0, 1, 2, 3]

        with Video(
            asset_dict['ref_path'], mode='r',
            standard=asset_dict['ref_standard'],
            width=asset_dict['width'], height=asset_dict['height']
        ) as v_ref:
            with Video(
                asset_dict['dis_path'], mode='r',
                standard=asset_dict['dis_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_dis:
                # w_crop = (v_ref.width >> self.wavelet_levels) << self.wavelet_levels
                # h_crop = (v_ref.height >> self.wavelet_levels) << self.wavelet_levels

                w_pad = ((v_ref.width + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels
                h_pad = ((v_ref.height + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels

                for frame_ind, (frame_ref, frame_dis) in enumerate(zip(v_ref, v_dis)):
                    start_time = time.time()
                    res_dict['Frame'].append(frame_ind)
                    prof_dict['Frame'].append(frame_ind)
                    
                    y_ref = frame_ref.yuv[..., 0] / asset_dict['ref_standard'].range
                    y_dis = frame_dis.yuv[..., 0] / asset_dict['dis_standard'].range

                    # # Cropping to a power of 2 to avoid problems in SSIM
                    # y_ref = y_ref[:h_crop, :w_crop]
                    # y_dis = y_dis[:h_crop, :w_crop]

                    # Padding to a power of 2 to avoid problems in SSIM
                    h_pad_amt = h_pad - y_ref.shape[0]
                    w_pad_amt = w_pad - y_ref.shape[1]
                    y_ref = np.pad(y_ref, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                    y_dis = np.pad(y_dis, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                    #print(y_ref.shape, y_dis.shape, v_ref.width, v_ref.height, self.wavelet_levels)

                    channel_ref = y_ref
                    channel_dis = y_dis

                    filters_start_time = time.time()
                    [channel_ref, channel_dis] = [filter_utils.filter_img(channel, self.csf, self.wavelet, channel=channel_ind) for channel in (channel_ref, channel_dis)]
                    filters_end_time = dwt_start_time = time.time()
                    [pyr_ref, pyr_dis] = [pyr_features.custom_wavedec2(channel, self.wavelet, 'periodization', self.wavelet_levels) for channel in (channel_ref, channel_dis)]
                    dwt_end_time = time.time()
                    
                    if frame_ind % sample_interval:
                        prev_pyr_ref = pyr_ref.copy()
                        prev_pyr_dis = pyr_dis.copy()
                        continue

                    # MS_SSIM features
                    ms_ssim_start_time = time.time()
                    (ms_ssim_mean_scales, _), (ms_ssim_cov_scales, _), (ms_ssim_mink_scales, _) = pyr_features.ms_ssim_pyr(pyr_ref, pyr_dis, pool='all')
                    ms_ssim_end_time = time.time()
                    feats_dict[f'ms_ssim_cov_channel_{channel_name}_levels_{self.wavelet_levels}'].append(ms_ssim_cov_scales[-1])
                    for level, mean, cov, mink in zip(levels, ms_ssim_mean_scales, ms_ssim_cov_scales, ms_ssim_mink_scales):
                        res_dict[f'FUNQUE_feature_ms_ssim_mean_scale{level}_score'].append(mean)
                        res_dict[f'FUNQUE_feature_ms_ssim_cov_scale{level}_score'].append(cov)
                        res_dict[f'FUNQUE_feature_ms_ssim_mink3_scale{level}_score'].append(mink)

                    # DLM features
                    dlm_start_time = time.time()    
                    dlm_val, dlm_level_wise_scores = pyr_features.dlm_pyr((None, [pyr_ref[1][-1]]), (None, [pyr_dis[1][-1]]), csf=None)
                    dlm_end_time = time.time()
                    feats_dict[f'dlm_channel_{channel_name}_scale_{self.wavelet_levels}'].append(dlm_val)
                    res_dict[f'FUNQUE_feature_adm_scale0_score'].append(dlm_val)

                    strred_start_time = time.time()
                    if frame_ind != 0:
                        # MAD features
                        #motion_val = np.mean(np.abs(pyr_dis[0][-1]- prev_pyr_dis[0][-1]))

                        # STRRED features
                        (_, _, strred_scales) = pyr_features.strred_hv_pyr(pyr_ref, pyr_dis, prev_pyr_ref, prev_pyr_dis, block_size=1)
                    else:
                        motion_val = 0 
                        strred_scales = [0]*self.wavelet_levels
                    strred_end_time = time.time()
                    
                    feats_dict[f'mad_dis_channel_{channel_name}_scale_{self.wavelet_levels}'].append(motion_val)
                    feats_dict[f'strred_scalar_channel_{channel_name}_levels_{self.wavelet_levels}'].append(strred_scales[-1])
                    for level, value in zip(levels, strred_scales):
                        res_dict[f'FUNQUE_feature_strred_scale{level}_score'].append(value)
                    '''
                    # TLVQM-like features 
                    # Spatial activity - swap Haar H, V for Sobel H, V
                    energy_ref = pyr_ref[1][-1][0]**2 + pyr_ref[1][-1][1]**2
                    energy_dis = pyr_dis[1][-1][0]**2 + pyr_dis[1][-1][1]**2

                    sai_ref = np.std(np.sqrt(energy_ref))**0.25
                    sai_dis = np.std(np.sqrt(energy_dis))**0.25

                    feats_dict[f'sai_diff_channel_{channel_name}_scale_{self.wavelet_levels}'].append(sai_ref - sai_dis)
                    '''
                    prev_pyr_ref = pyr_ref
                    prev_pyr_dis = pyr_dis

                    end_time = time.time()
                    prof_dict['time_taken'].append(end_time - start_time)
                    prof_dict['resizer'].append(0)
                    prof_dict['filters'].append(filters_end_time - filters_start_time)
                    prof_dict['dwt'].append(dwt_end_time - dwt_start_time)
                    prof_dict['ms_ssim'].append(ms_ssim_end_time - ms_ssim_start_time)
                    prof_dict['adm'].append(dlm_end_time - dlm_start_time)
                    prof_dict['strred'].append(strred_end_time - strred_start_time)
                 
        prof_data = {k: pd.Series(v + ['Sum'] if k == 'Frame' else v + [sum(map(float, v))]) for k, v in prof_dict.items()}
        prof_df = pd.DataFrame(prof_data)
        prof_df.to_csv(asset_dict['profile_file'], index=False)
        
        data = {k: pd.Series(v) for k, v in res_dict.items()}
        res_df = pd.DataFrame(data)
        res_df.to_csv(asset_dict['out_file'], index=False)
        
        feats = np.array(list(feats_dict.values())).T
        print(f'Processed {asset_dict["dis_path"]}')
        return self._to_result(asset_dict, feats, list(feats_dict.keys()))


class ThreeChannelFunquePlusFeatureExtractor(FeatureExtractor):
    '''
    A feature extractor that implements FS-Y-FUNQUE+.
    '''
    NAME = '3C_FUNQUE_Plus_fex'
    VERSION = '1.0'

    def __init__(self, use_cache: bool = True, sample_rate: Optional[int] = None) -> None:
        super().__init__(use_cache, sample_rate)
        self.wavelet_levels = 2
        self.csf = 'li'
        self.wavelet = 'haar'
        self.feat_names = \
            [f'ms_ssim_cov_channel_y_levels_{self.wavelet_levels}', f'srred_scalar_channel_y_levels_{self.wavelet_levels}', f'trred_scalar_channel_y_levels_{self.wavelet_levels}'] + \
            [f'dlm_channel_y_scale_{self.wavelet_levels}', f'mad_dis_channel_y_scale_{self.wavelet_levels}'] + \
            [f'edge_channel_u_scale_{self.wavelet_levels}', f'mad_channel_v_scale_{self.wavelet_levels}']

    def _run_on_asset(self, asset_dict: Dict[str, Any]) -> Result:
        sample_interval = self._get_sample_interval(asset_dict)
        feats_dict = {key: [] for key in self.feat_names}

        channel_names = ['y', 'u', 'v']

        with Video(
            asset_dict['ref_path'], mode='r',
            standard=asset_dict['ref_standard'],
            width=asset_dict['width'], height=asset_dict['height']
        ) as v_ref:
            with Video(
                asset_dict['dis_path'], mode='r',
                standard=asset_dict['dis_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_dis:
                # w_crop = (v_ref.width >> (self.wavelet_levels+1)) << self.wavelet_levels
                # h_crop = (v_ref.height >> (self.wavelet_levels+1)) << self.wavelet_levels

                w_pad = (((v_ref.width//2) + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels
                h_pad = (((v_ref.height//2) + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels

                pyrs_ref = {}
                pyrs_dis = {}
                for frame_ind, (frame_ref, frame_dis) in enumerate(zip(v_ref, v_dis)):
                    for channel_ind, channel_name in enumerate(channel_names):
                        channel_ref = cv2.resize(frame_ref.yuv[..., channel_ind].astype(v_ref.standard.dtype), (frame_ref.width//2, frame_ref.height//2), interpolation=cv2.INTER_CUBIC) / asset_dict['ref_standard'].range
                        channel_dis = cv2.resize(frame_dis.yuv[..., channel_ind].astype(v_dis.standard.dtype), (frame_dis.width//2, frame_dis.height//2), interpolation=cv2.INTER_CUBIC) / asset_dict['dis_standard'].range

                        # channel_ref = channel_ref[:h_crop, :w_crop]
                        # channel_dis = channel_dis[:h_crop, :w_crop]

                        # Padding to a power of 2 to avoid problems in SSIM
                        h_pad_amt = h_pad - channel_ref.shape[0]
                        w_pad_amt = w_pad - channel_ref.shape[1]
                        channel_ref = np.pad(channel_ref, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                        channel_dis = np.pad(channel_dis, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                        print(channel_ref.shape, channel_dis.shape, v_ref.width, v_ref.height, self.wavelet_levels)

                        [pyr_ref, pyr_dis] = [pyr_features.custom_wavedec2(channel, self.wavelet, 'periodization', self.wavelet_levels) for channel in (channel_ref, channel_dis)]
                        [pyr_ref, pyr_dis] = [filter_utils.filter_pyr(pyr, self.csf, channel=channel_ind) for pyr in (pyr_ref, pyr_dis)]

                        pyrs_ref[channel_name] = pyr_ref
                        pyrs_dis[channel_name] = pyr_dis

                    if frame_ind % sample_interval:
                        prev_pyrs_ref = pyrs_ref.copy()
                        prev_pyrs_dis = pyrs_dis.copy()
                        continue

                    # Y channel
                    channel_name = 'y'
                    channel_ind = 0
                    pyr_ref = pyrs_ref[channel_name]
                    pyr_dis = pyrs_dis[channel_name]

                    # SSIM features
                    ms_ssim_cov_scales, _ = pyr_features.ms_ssim_pyr(pyr_ref, pyr_dis, pool='cov')
                    feats_dict[f'ms_ssim_cov_channel_{channel_name}_levels_{self.wavelet_levels}'].append(ms_ssim_cov_scales[-1])

                    # DLM features
                    dlm_val = pyr_features.dlm_pyr((None, [pyr_ref[1][-1]]), (None, [pyr_dis[1][-1]]), csf=None)
                    feats_dict[f'dlm_channel_{channel_name}_scale_{self.wavelet_levels}'].append(dlm_val)

                    if frame_ind != 0:
                        # MAD features
                        mad_dis_val = np.mean(np.abs(pyr_dis[0][-1] - prev_pyrs_dis[channel_name][0][-1]))

                        # Scalar ST-RRED features
                        srred_scales, trred_scales, _ = pyr_features.strred_hv_pyr(pyr_ref, pyr_dis, prev_pyrs_ref[channel_name], prev_pyrs_dis[channel_name], block_size=1)
                    else:
                        mad_dis_val = 0
                        srred_scales = [0]*self.wavelet_levels
                        trred_scales = [0]*self.wavelet_levels

                    feats_dict[f'mad_dis_channel_{channel_name}_scale_{self.wavelet_levels}'].append(mad_dis_val)

                    feats_dict[f'srred_scalar_channel_{channel_name}_levels_{self.wavelet_levels}'].append(srred_scales[-1])
                    feats_dict[f'trred_scalar_channel_{channel_name}_levels_{self.wavelet_levels}'].append(trred_scales[-1])

                    # U channel
                    channel_name = 'u'
                    channel_ind = 1

                    pyr_ref = pyrs_ref[channel_name]
                    pyr_dis = pyrs_dis[channel_name]

                    [edge_val] = pyr_features.blur_edge_pyr((None, [pyr_ref[1][-1]]), (None, [pyr_dis[1][-1]]), mode='edge')
                    feats_dict[f'edge_channel_{channel_name}_scale_{self.wavelet_levels}'].append(edge_val)

                    # V channel
                    channel_name = 'v'
                    channel_ind = 2
                    pyr_ref = pyrs_ref[channel_name]
                    pyr_dis = pyrs_dis[channel_name]

                    feats_dict[f'mad_channel_{channel_name}_scale_{self.wavelet_levels}'].append(np.mean(np.abs(pyr_ref[0][-1] - pyr_dis[0][-1])))

                    prev_pyrs_ref = pyrs_ref.copy()
                    prev_pyrs_dis = pyrs_dis.copy()

        feats = np.array(list(feats_dict.values())).T
        print(f'Processed {asset_dict["dis_path"]}')
        return self._to_result(asset_dict, feats, list(feats_dict.keys()))


class FullScaleThreeChannelFunquePlusFeatureExtractor(FeatureExtractor):
    '''
    A feature extractor that implements FS-Y-FUNQUE+.
    '''
    NAME = 'FS_3C_FUNQUE_Plus_fex'
    VERSION = '1.0'

    def __init__(self, use_cache: bool = True, sample_rate: Optional[int] = None) -> None:
        super().__init__(use_cache, sample_rate)
        self.wavelet_levels = 3
        self.csf = 'watson'
        self.wavelet = 'haar'
        self.feat_names = \
            [f'ms_ssim_cov_channel_y_levels_{self.wavelet_levels}', f'dlm_channel_y_scale_{self.wavelet_levels}', f'sai_diff_channel_y_scale_{self.wavelet_levels}'] + \
            [f'mad_dis_channel_u_scale_{self.wavelet_levels}', f'srred_scalar_channel_u_levels_{self.wavelet_levels}', f'trred_scalar_channel_u_levels_{self.wavelet_levels}', f'edge_channel_u_scale_{self.wavelet_levels}'] + \
            [f'mad_channel_v_scale_{self.wavelet_levels}', f'blur_channel_v_scale_{self.wavelet_levels}']

    def _run_on_asset(self, asset_dict: Dict[str, Any]) -> Result:
        sample_interval = self._get_sample_interval(asset_dict)
        feats_dict = {key: [] for key in self.feat_names}

        channel_names = ['y', 'u', 'v']

        with Video(
            asset_dict['ref_path'], mode='r',
            standard=asset_dict['ref_standard'],
            width=asset_dict['width'], height=asset_dict['height']
        ) as v_ref:
            with Video(
                asset_dict['dis_path'], mode='r',
                standard=asset_dict['dis_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_dis:
                # w_crop = (v_ref.width >> self.wavelet_levels) << self.wavelet_levels
                # h_crop = (v_ref.height >> self.wavelet_levels) << self.wavelet_levels

                w_pad = ((v_ref.width + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels
                h_pad = ((v_ref.height + 2**self.wavelet_levels-1) >> self.wavelet_levels) << self.wavelet_levels

                pyrs_ref = {}
                pyrs_dis = {}
                for frame_ind, (frame_ref, frame_dis) in enumerate(zip(v_ref, v_dis)):
                    for channel_ind, channel_name in enumerate(channel_names):
                        channel_ref = frame_ref.yuv[..., channel_ind] / asset_dict['ref_standard'].range
                        channel_dis = frame_dis.yuv[..., channel_ind] / asset_dict['dis_standard'].range

                        # channel_ref = channel_ref[:h_crop, :w_crop]
                        # channel_dis = channel_dis[:h_crop, :w_crop]

                        # Padding to a power of 2 to avoid problems in SSIM
                        h_pad_amt = h_pad - channel_ref.shape[0]
                        w_pad_amt = w_pad - channel_ref.shape[1]
                        channel_ref = np.pad(channel_ref, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                        channel_dis = np.pad(channel_dis, [(h_pad_amt//2, h_pad_amt-h_pad_amt//2), (w_pad_amt//2, w_pad_amt-w_pad_amt//2)], mode='reflect')
                        print(channel_ref.shape, channel_dis.shape, v_ref.width, v_ref.height, self.wavelet_levels)

                        [pyr_ref, pyr_dis] = [pyr_features.custom_wavedec2(channel, self.wavelet, 'periodization', self.wavelet_levels) for channel in (channel_ref, channel_dis)]
                        [pyr_ref, pyr_dis] = [filter_utils.filter_pyr(pyr, self.csf, channel=channel_ind) for pyr in (pyr_ref, pyr_dis)]

                        pyrs_ref[channel_name] = pyr_ref
                        pyrs_dis[channel_name] = pyr_dis

                    if frame_ind % sample_interval:
                        prev_pyrs_ref = pyrs_ref.copy()
                        prev_pyrs_dis = pyrs_dis.copy()
                        continue

                    # Y channel
                    channel_name = 'y'
                    channel_ind = 0
                    pyr_ref = pyrs_ref[channel_name]
                    pyr_dis = pyrs_dis[channel_name]

                    # SSIM features
                    ms_ssim_cov_scales, _ = pyr_features.ms_ssim_pyr(pyr_ref, pyr_dis, pool='cov')
                    feats_dict[f'ms_ssim_cov_channel_{channel_name}_levels_{self.wavelet_levels}'].append(ms_ssim_cov_scales[-1])

                    # TLVQM-like features 
                    # Spatial activity - swap Haar H, V for Sobel H, V
                    energy_ref = pyr_ref[1][-1][0]**2 + pyr_ref[1][-1][1]**2
                    energy_dis = pyr_dis[1][-1][0]**2 + pyr_dis[1][-1][1]**2

                    sai_ref = np.std(np.sqrt(energy_ref))**0.25
                    sai_dis = np.std(np.sqrt(energy_dis))**0.25

                    feats_dict[f'sai_diff_channel_{channel_name}_scale_{self.wavelet_levels}'].append(sai_ref - sai_dis)

                    # DLM features
                    dlm_val = pyr_features.dlm_pyr((None, [pyr_ref[1][-1]]), (None, [pyr_dis[1][-1]]), csf=None)
                    feats_dict[f'dlm_channel_{channel_name}_scale_{self.wavelet_levels}'].append(dlm_val)

                    # U channel
                    channel_name = 'u'
                    channel_ind = 1
                    pyr_ref = pyrs_ref[channel_name]
                    pyr_dis = pyrs_dis[channel_name]

                    if frame_ind != 0:
                        # MAD-Dis features
                        mad_dis_val = np.mean(np.abs(pyr_dis[0][-1] - prev_pyrs_dis[channel_name][0][-1]))
                        # Scalar ST-RRED features
                        srred_scales, trred_scales, _ = pyr_features.strred_hv_pyr(pyr_ref, pyr_dis, prev_pyrs_ref[channel_name], prev_pyrs_dis[channel_name], block_size=1)
                    else:
                        mad_dis_val = 0
                        srred_scales = [0]*self.wavelet_levels
                        trred_scales = [0]*self.wavelet_levels

                    feats_dict[f'mad_dis_channel_{channel_name}_scale_{self.wavelet_levels}'].append(mad_dis_val)

                    feats_dict[f'srred_scalar_channel_{channel_name}_levels_{self.wavelet_levels}'].append(srred_scales[-1])
                    feats_dict[f'trred_scalar_channel_{channel_name}_levels_{self.wavelet_levels}'].append(trred_scales[-1])

                    # Edge features
                    [edge_val] = pyr_features.blur_edge_pyr((None, [pyr_ref[1][-1]]), (None, [pyr_dis[1][-1]]), mode='edge')
                    feats_dict[f'edge_channel_{channel_name}_scale_{self.wavelet_levels}'].append(edge_val)

                    # V channel
                    channel_name = 'v'
                    channel_ind = 2
                    pyr_ref = pyrs_ref[channel_name]
                    pyr_dis = pyrs_dis[channel_name]

                    feats_dict[f'mad_channel_{channel_name}_scale_{self.wavelet_levels}'].append(np.mean(np.abs(pyr_ref[0][-1] - pyr_dis[0][-1])))

                    # Blur features
                    [blur_val] = pyr_features.blur_edge_pyr((None, [pyr_ref[1][-1]]), (None, [pyr_dis[1][-1]]), mode='blur')
                    feats_dict[f'blur_channel_{channel_name}_scale_{self.wavelet_levels}'].append(blur_val)

                    prev_pyrs_ref = pyrs_ref.copy()
                    prev_pyrs_dis = pyrs_dis.copy()

        feats = np.array(list(feats_dict.values())).T
        print(f'Processed {asset_dict["dis_path"]}')
        return self._to_result(asset_dict, feats, list(feats_dict.keys()))


class VmafLikeFeatureExtractor(FeatureExtractor):
    '''
    A feature extractor that implements VMAF using FUNQUE features.
    '''
    NAME = 'VMAF_Like_fex'
    VERSION = '1.0'
    res_names = ['Frame','FUNQUE_feature_adm_score', 'FUNQUE_feature_adm_scale0_score', 'FUNQUE_feature_adm_scale1_score', 'FUNQUE_feature_adm_scale2_score', 'FUNQUE_feature_adm_scale3_score',
                'FUNQUE_feature_mad_scale0_score', 'FUNQUE_feature_vif_scale0_score','FUNQUE_feature_vif_scale1_score','FUNQUE_feature_vif_scale2_score','FUNQUE_feature_vif_scale3_score']
    prof_feat =['Frame','time_taken','resizer','filters','dwt','vif','adm','mad']    
    def __init__(self, use_cache: bool = True, sample_rate: Optional[int] = None) -> None:
        super().__init__(use_cache, sample_rate)
        self.wavelet_levels = 4
        self.csf = 'nadenau_weight'
        self.wavelet = 'haar'
        self.feat_names = \
            [f'dlm_channel_y_levels_{self.wavelet_levels}', f'motion_channel_y_scale_{self.wavelet_levels}'] + \
            [f'vif_approx_scalar_channel_y_scale_{scale+1}' for scale in range(self.wavelet_levels)]

    def _run_on_asset(self, asset_dict: Dict[str, Any]) -> Result:
        sample_interval = self._get_sample_interval(asset_dict)
        feats_dict = {key: [] for key in self.feat_names}
        res_dict = {key: [] for key in self.res_names}
        prof_dict = {key: [] for key in self.prof_feat}

        channel_names = ['y', 'u', 'v']
        channel_name = 'y'
        channel_ind = 0

        if self.wavelet_levels:
            levels = [0, 1, 2, 3]
        with Video(
            asset_dict['ref_path'], mode='r',
            standard=asset_dict['ref_standard'],
            width=asset_dict['width'], height=asset_dict['height']
        ) as v_ref:
            with Video(
                asset_dict['dis_path'], mode='r',
                standard=asset_dict['dis_standard'],
                width=asset_dict['width'], height=asset_dict['height']
            ) as v_dis:
                w_crop = (v_ref.width >> (self.wavelet_levels)) << self.wavelet_levels
                h_crop = (v_ref.height >> (self.wavelet_levels)) << self.wavelet_levels
                for frame_ind, (frame_ref, frame_dis) in enumerate(zip(v_ref, v_dis)):
                    start_time = time.time()
                    res_dict['Frame'].append(frame_ind)
                    prof_dict['Frame'].append(frame_ind)

                    y_ref = frame_ref.yuv[..., 0].astype('float64')/asset_dict['ref_standard'].range
                    y_dis = frame_dis.yuv[..., 0].astype('float64')/asset_dict['dis_standard'].range

                    y_ref = y_ref[:h_crop, :w_crop]
                    y_dis = y_dis[:h_crop, :w_crop]

                    channel_ref = y_ref
                    channel_dis = y_dis

                    dwt_start_time = time.time()
                    [pyr_ref, pyr_dis] = [pyr_features.custom_wavedec2(channel, self.wavelet, 'periodization', self.wavelet_levels) for channel in (channel_ref, channel_dis)]
                    dwt_end_time = filters_start_time = time.time()
                    [pyr_ref, pyr_dis] = [filter_utils.filter_pyr(pyr, self.csf, channel=channel_ind) for pyr in (pyr_ref, pyr_dis)]
                    filters_end_time = time.time()
                    
                    if frame_ind % sample_interval:
                        prev_pyr_ref = pyr_ref.copy()
                        continue

                    # Scalar VIF features
                    vif_start_time = time.time()
                    vif_approx_scales = [vif_utils.vif_spatial(approx_ref, approx_dis, sigma_nsq=5, k=9, full=False) for approx_ref, approx_dis in zip(pyr_ref[0], pyr_dis[0])]
                    vif_end_time = time.time()
                    for lev, vif_approx_scale in enumerate(vif_approx_scales):
                        feats_dict[f'vif_approx_scalar_channel_{channel_name}_scale_{lev+1}'].append(vif_approx_scale)
                    for level, value in zip(levels, vif_approx_scales):
                        res_dict[f'FUNQUE_feature_vif_scale{level}_score'].append(value) 

                    # DLM features
                    dlm_start_time = time.time()
                    dlm_val, dlm_level_wise_scores = pyr_features.dlm_pyr(pyr_ref, pyr_dis, csf=None)
                    dlm_end_time = time.time()
                    feats_dict[f'dlm_channel_{channel_name}_levels_{self.wavelet_levels}'].append(dlm_val)
                    res_dict[f'FUNQUE_feature_adm_score'].append(dlm_val)
                    for level, value in zip(levels, dlm_level_wise_scores):
                        res_dict[f'FUNQUE_feature_adm_scale{level}_score'].append(value) 
                     
                    # MAD features
                    mad_start_time = time.time()
                    if frame_ind != 0:
                        subband = pyr_ref[0][0]
                        prev_subband = prev_pyr_ref[0][0]
                        motion_val = np.mean(np.abs(subband - prev_subband))
                    else:
                        motion_val = 0
                    mad_end_time = time.time()
                    feats_dict[f'motion_channel_{channel_name}_scale_{self.wavelet_levels}'].append(motion_val)
                    res_dict[f'FUNQUE_feature_mad_scale0_score'].append(motion_val)                     
                    prev_pyr_ref = pyr_ref
    
                    end_time = time.time()
                    prof_dict['time_taken'].append(end_time - start_time)
                    prof_dict['resizer'].append(0)
                    prof_dict['filters'].append(filters_end_time - filters_start_time)
                    prof_dict['dwt'].append(dwt_end_time - dwt_start_time)
                    prof_dict['vif'].append(vif_end_time - vif_start_time)
                    prof_dict['adm'].append(dlm_end_time - dlm_start_time)
                    prof_dict['mad'].append(mad_end_time - mad_start_time)
                 
        prof_data = {k: pd.Series(v + ['Sum'] if k == 'Frame' else v + [sum(map(float, v))]) for k, v in prof_dict.items()}
        prof_df = pd.DataFrame(prof_data)
        prof_df.to_csv(asset_dict['profile_file'], index=False)
                    
        data = {k: pd.Series(v) for k, v in res_dict.items()}
        res_df = pd.DataFrame(data)
        res_df.to_csv(asset_dict['out_file'], index=False)

        feats = np.array(list(feats_dict.values())).T
        print(f'Processed {asset_dict["dis_path"]}')
        return self._to_result(asset_dict, feats, list(feats_dict.keys()))
