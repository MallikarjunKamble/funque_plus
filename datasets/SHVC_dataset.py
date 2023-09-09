from videolib import standards

dataset_name = 'SHVC'

dataset_dir = '[path to dataset]'

ref_videos = {
    1: {
     'content_name': 'BirthdayLucy',
     'width': 1920,
     'height': 1080,
     'standard': standards.rec_2020,
     'path': dataset_dir + '/ref/Session1/Session1_WCG_BirthdayLucy_1920x1080p60_10b.yuv',
     },
    2: {
     'content_name': 'Parakeets',
     'width': 1920,
     'height': 1080,
     'standard': standards.rec_2020,
     'path': dataset_dir + '/ref/Session1/Session1_WCG_Parakeets500_1920x1080p50_10b.yuv',
     },
    3: {
     'content_name': 'HDR_Market',
     'width': 1920,
     'height': 1080,
     'standard': standards.rec_2100_pq,  # Guessing, though reading and using only YUV will be fine despite mismatches
     'path': dataset_dir + '/ref/Session2/Session2_HDR_Market_1920x1080p50_10b.yuv',
     },
    4: {
     'content_name': 'HDR_BalloonFestival',
     'width': 1920,
     'height': 1080,
     'standard': standards.rec_2100_pq,  # Guessing, though reading and using only YUV will be fine despite mismatches
     'path': dataset_dir + '/ref/Session2/Session2_HDR_BalloonFestival_1920x1080p24_10b.yuv',
     },
    5: {
     'content_name': 'ElFuente_12000_12600',
     'width': 3820,
     'height': 2160,
     'standard': standards.sRGB,
     'path': dataset_dir + '/ref/Session3/Session3_ElFuente_12000_12600_Crop_3840x2160_5994fps_420_8b.yuv',
     },
    6: {
     'content_name': 'ElFuente_14900_15500',
     'width': 3820,
     'height': 2160,
     'standard': standards.sRGB,
     'path': dataset_dir + '/ref/Session3/Session3_ElFuente_14900_15500_Crop_3840x2160_5994fps_420_8b.yuv',
     },
    7: {
     'content_name': 'Bbscorecheer',
     'width': 1920,
     'height': 1080,
     'stabdard': standards.sRGB,
     'path': dataset_dir + '/ref/Session4/Session4_bbscorecheer_1920x1080p30_420_8b.yuv',
     },
    8: {
     'content_name': 'Underboat1',
     'width': 1920,
     'height': 1080,
     'stabdard': standards.sRGB,
     'path': dataset_dir + '/ref/Session4/Session4_underboat1_1920x1080p30_420_8b.yuv',
     },
    9: {
     'content_name': 'Vidyo5',
     'width': 1920,
     'height': 1080,
     'standard': standards.sRGB,
     'path': dataset_dir + '/ref/Session4/Session4_vidyo5_1920x1080p30_8b.yuv',
     },
    10: {
     'content_name': 'Vidyo6',
     'width': 1920,
     'height': 1080,
     'standard': standards.sRGB,
     'path': dataset_dir + '/ref/Session4/Session4_vidyo6_1920x1080p30_8b.yuv',
     },
}

dis_videos_session1 = {
    1: {
     'content_id': 1,
     'groundtruth': 7.83,
     'path': dataset_dir + '/dis/Session1/P01S01C4R1.yuv',
    },
    2: {
     'content_id': 1,
     'groundtruth': 7.00,
     'path': dataset_dir + '/dis/Session1/P01S01C4R2.yuv',
    },
    3: {
     'content_id': 1,
     'groundtruth': 4.46,
     'path': dataset_dir + '/dis/Session1/P01S01C4R3.yuv',
    },
    4: {
     'content_id': 1,
     'groundtruth': 3.08,
     'path': dataset_dir + '/dis/Session1/P01S01C4R4.yuv',
    },

    5: {
     'content_id': 2,
     'groundtruth': 9.13,
     'path': dataset_dir + '/dis/Session1/P01S02C4R1.yuv',
    },
    6: {
     'content_id': 2,
     'groundtruth': 8.21,
     'path': dataset_dir + '/dis/Session1/P01S02C4R2.yuv',
    },
    7: {
     'content_id': 2,
     'groundtruth': 6.13,
     'path': dataset_dir + '/dis/Session1/P01S02C4R3.yuv',
    },
    8: {
     'content_id': 2,
     'groundtruth': 3.58,
     'path': dataset_dir + '/dis/Session1/P01S02C4R4.yuv',
    },

    9: {
     'content_id': 1,
     'groundtruth': 8.63,
     'path': dataset_dir + '/dis/Session1/P02S01C4R1.yuv',
    },
    10: {
     'content_id': 1,
     'groundtruth': 7.42,
     'path': dataset_dir + '/dis/Session1/P02S01C4R2.yuv',
    },
    11: {
     'content_id': 1,
     'groundtruth': 5.83,
     'path': dataset_dir + '/dis/Session1/P02S01C4R3.yuv',
    },
    12: {
     'content_id': 1,
     'groundtruth': 3.58,
     'path': dataset_dir + '/dis/Session1/P02S01C4R4.yuv',
    },

    13: {
     'content_id': 2,
     'groundtruth': 9.21,
     'path': dataset_dir + '/dis/Session1/P02S02C4R1.yuv',
    },
    14: {
     'content_id': 2,
     'groundtruth': 8.38,
     'path': dataset_dir + '/dis/Session1/P02S02C4R2.yuv',
    },
    15: {
     'content_id': 2,
     'groundtruth': 6.71,
     'path': dataset_dir + '/dis/Session1/P02S02C4R3.yuv',
    },
    16: {
     'content_id': 2,
     'groundtruth': 4.25,
     'path': dataset_dir + '/dis/Session1/P02S02C4R4.yuv',
    },
}

dis_videos_session2 = {
    17: {
     'content_id': 3,
     'groundtruth': 8.08,
     'path': dataset_dir + '/dis/Session2/P01S03C4R1.yuv',
    },
    18: {
     'content_id': 3,
     'groundtruth': 7.42,
     'path': dataset_dir + '/dis/Session2/P01S03C4R2.yuv',
    },
    19: {
     'content_id': 3,
     'groundtruth': 4.67,
     'path': dataset_dir + '/dis/Session2/P01S03C4R3.yuv',
    },
    20: {
     'content_id': 3,
     'groundtruth': 2.58,
     'path': dataset_dir + '/dis/Session2/P01S03C4R4.yuv',
    },

    21: {
     'content_id': 4,
     'groundtruth': 7.71,
     'path': dataset_dir + '/dis/Session2/P01S04C4R1.yuv',
    },
    22: {
     'content_id': 4,
     'groundtruth': 6.88,
     'path': dataset_dir + '/dis/Session2/P01S04C4R2.yuv',
    },
    23: {
     'content_id': 4,
     'groundtruth': 5.08,
     'path': dataset_dir + '/dis/Session2/P01S04C4R3.yuv',
    },
    24: {
     'content_id': 4,
     'groundtruth': 3.29,
     'path': dataset_dir + '/dis/Session2/P01S04C4R4.yuv',
    },

    25: {
     'content_id': 3,
     'groundtruth': 9.25,
     'path': dataset_dir + '/dis/Session2/P02S03C4R1.yuv',
    },
    26: {
     'content_id': 3,
     'groundtruth': 7.67,
     'path': dataset_dir + '/dis/Session2/P02S03C4R2.yuv',
    },
    27: {
     'content_id': 3,
     'groundtruth': 5.63,
     'path': dataset_dir + '/dis/Session2/P02S03C4R3.yuv',
    },
    28: {
     'content_id': 3,
     'groundtruth': 3.71,
     'path': dataset_dir + '/dis/Session2/P02S03C4R4.yuv',
    },

    29: {
     'content_id': 4,
     'groundtruth': 8.21,
     'path': dataset_dir + '/dis/Session2/P02S04C4R1.yuv',
    },
    30: {
     'content_id': 4,
     'groundtruth': 7.38,
     'path': dataset_dir + '/dis/Session2/P02S04C4R2.yuv',
    },
    31: {
     'content_id': 4,
     'groundtruth': 5.83,
     'path': dataset_dir + '/dis/Session2/P02S04C4R3.yuv',
    },
    32: {
     'content_id': 4,
     'groundtruth': 3.67,
     'path': dataset_dir + '/dis/Session2/P02S04C4R4.yuv',
    },
}

dis_videos_session3 = {
    33: {
     'content_id': 5,
     'groundtruth': 8.67,
     'path': dataset_dir + '/dis/Session3/P01S05C1R1.yuv',
    },
    34: {
     'content_id': 5,
     'groundtruth': 6.42,
     'path': dataset_dir + '/dis/Session3/P01S05C1R2.yuv',
    },
    35: {
     'content_id': 5,
     'groundtruth': 3.13,
     'path': dataset_dir + '/dis/Session3/P01S05C1R3.yuv',
    },
    36: {
     'content_id': 5,
     'groundtruth': 0.42,
     'path': dataset_dir + '/dis/Session3/P01S05C1R4.yuv',
    },

    37: {
     'content_id': 6,
     'groundtruth': 9.04,
     'path': dataset_dir + '/dis/Session3/P01S06C1R1.yuv',
    },
    38: {
     'content_id': 6,
     'groundtruth': 7.88,
     'path': dataset_dir + '/dis/Session3/P01S06C1R2.yuv',
    },
    39: {
     'content_id': 6,
     'groundtruth': 5.08,
     'path': dataset_dir + '/dis/Session3/P01S06C1R3.yuv',
    },
    40: {
     'content_id': 6,
     'groundtruth': 1.54,
     'path': dataset_dir + '/dis/Session3/P01S06C1R4.yuv',
    },

    41: {
     'content_id': 5,
     'groundtruth': 8.38,
     'path': dataset_dir + '/dis/Session3/P01S07C2R1.yuv',
    },
    42: {
     'content_id': 5,
     'groundtruth': 6.83,
     'path': dataset_dir + '/dis/Session3/P01S07C2R2.yuv',
    },
    43: {
     'content_id': 5,
     'groundtruth': 4.29,
     'path': dataset_dir + '/dis/Session3/P01S07C2R3.yuv',
    },
    44: {
     'content_id': 5,
     'groundtruth': 0.54,
     'path': dataset_dir + '/dis/Session3/P01S07C2R4.yuv',
    },

    45: {
     'content_id': 6,
     'groundtruth': 9.00,
     'path': dataset_dir + '/dis/Session3/P01S08C3R1.yuv',
    },
    46: {
     'content_id': 6,
     'groundtruth': 7.13,
     'path': dataset_dir + '/dis/Session3/P01S08C3R2.yuv',
    },
    47: {
     'content_id': 6,
     'groundtruth': 4.50,
     'path': dataset_dir + '/dis/Session3/P01S08C3R3.yuv',
    },
    48: {
     'content_id': 6,
     'groundtruth': 1.58,
     'path': dataset_dir + '/dis/Session3/P01S08C3R4.yuv',
    },

    49: {
     'content_id': 5,
     'groundtruth': 8.67,
     'path': dataset_dir + '/dis/Session3/P02S05C1R1.yuv',
    },
    50: {
     'content_id': 5,
     'groundtruth': 7.17,
     'path': dataset_dir + '/dis/Session3/P02S05C1R2.yuv',
    },
    51: {
     'content_id': 5,
     'groundtruth': 3.63,
     'path': dataset_dir + '/dis/Session3/P02S05C1R3.yuv',
    },
    52: {
     'content_id': 5,
     'groundtruth': 0.92,
     'path': dataset_dir + '/dis/Session3/P02S05C1R4.yuv',
    },

    53: {
     'content_id': 6,
     'groundtruth': 8.96,
     'path': dataset_dir + '/dis/Session3/P02S06C1R1.yuv',
    },
    54: {
     'content_id': 6,
     'groundtruth': 7.83,
     'path': dataset_dir + '/dis/Session3/P02S06C1R2.yuv',
    },
    55: {
     'content_id': 6,
     'groundtruth': 5.71,
     'path': dataset_dir + '/dis/Session3/P02S06C1R3.yuv',
    },
    56: {
     'content_id': 6,
     'groundtruth': 2.54,
     'path': dataset_dir + '/dis/Session3/P02S06C1R4.yuv',
    },

    57: {
     'content_id': 5,
     'groundtruth': 8.88,
     'path': dataset_dir + '/dis/Session3/P02S07C2R1.yuv',
    },
    58: {
     'content_id': 5,
     'groundtruth': 7.00,
     'path': dataset_dir + '/dis/Session3/P02S07C2R2.yuv',
    },
    59: {
     'content_id': 5,
     'groundtruth': 4.50,
     'path': dataset_dir + '/dis/Session3/P02S07C2R3.yuv',
    },
    60: {
     'content_id': 5,
     'groundtruth': 1.71,
     'path': dataset_dir + '/dis/Session3/P02S07C2R4.yuv',
    },

    61: {
     'content_id': 6,
     'groundtruth': 9.25,
     'path': dataset_dir + '/dis/Session3/P02S08C3R1.yuv',
    },
    62: {
     'content_id': 6,
     'groundtruth': 7.83,
     'path': dataset_dir + '/dis/Session3/P02S08C3R2.yuv',
    },
    63: {
     'content_id': 6,
     'groundtruth': 5.63,
     'path': dataset_dir + '/dis/Session3/P02S08C3R3.yuv',
    },
    64: {
     'content_id': 6,
     'groundtruth': 2.25,
     'path': dataset_dir + '/dis/Session3/P02S08C3R4.yuv',
    },
}

dis_videos_session4 = {
    65: {
     'content_id': 10,
     'groundtruth': 7.79,
     'path': dataset_dir + '/dis/Session4/P01S09C1R1.yuv',
    },
    66: {
     'content_id': 10,
     'groundtruth': 5.13,
     'path': dataset_dir + '/dis/Session4/P01S09C1R2.yuv',
    },
    67: {
     'content_id': 10,
     'groundtruth': 3.04,
     'path': dataset_dir + '/dis/Session4/P01S09C1R3.yuv',
    },
    68: {
     'content_id': 10,
     'groundtruth': 0.88,
     'path': dataset_dir + '/dis/Session4/P01S09C1R4.yuv',
    },

    69: {
     'content_id': 9,
     'groundtruth': 7.67,
     'path': dataset_dir + '/dis/Session4/P01S10C2R1.yuv',
    },
    70: {
     'content_id': 9,
     'groundtruth': 5.75,
     'path': dataset_dir + '/dis/Session4/P01S10C2R2.yuv',
    },
    71: {
     'content_id': 9,
     'groundtruth': 4.08,
     'path': dataset_dir + '/dis/Session4/P01S10C2R3.yuv',
    },
    72: {
     'content_id': 9,
     'groundtruth': 1.75,
     'path': dataset_dir + '/dis/Session4/P01S10C2R4.yuv',
    },

    73: {
     'content_id': 7,
     'groundtruth': 8.21,
     'path': dataset_dir + '/dis/Session4/P01S11C2R1.yuv',
    },
    74: {
     'content_id': 7,
     'groundtruth': 7.13,
     'path': dataset_dir + '/dis/Session4/P01S11C2R2.yuv',
    },
    75: {
     'content_id': 7,
     'groundtruth': 5.04,
     'path': dataset_dir + '/dis/Session4/P01S11C2R3.yuv',
    },
    76: {
     'content_id': 7,
     'groundtruth': 3.21,
     'path': dataset_dir + '/dis/Session4/P01S11C2R4.yuv',
    },

    77: {
     'content_id': 8,
     'groundtruth': 8.42,
     'path': dataset_dir + '/dis/Session4/P01S12C3R1.yuv',
    },
    78: {
     'content_id': 8,
     'groundtruth': 6.46,
     'path': dataset_dir + '/dis/Session4/P01S12C3R2.yuv',
    },
    79: {
     'content_id': 8,
     'groundtruth': 2.92,
     'path': dataset_dir + '/dis/Session4/P01S12C3R3.yuv',
    },
    80: {
     'content_id': 8,
     'groundtruth': 0.08,
     'path': dataset_dir + '/dis/Session4/P01S12C3R4.yuv',
    },

    81: {
     'content_id': 10,
     'groundtruth': 8.67,
     'path': dataset_dir + '/dis/Session4/P02S09C1R1.yuv',
    },
    82: {
     'content_id': 10,
     'groundtruth': 5.96,
     'path': dataset_dir + '/dis/Session4/P02S09C1R2.yuv',
    },
    83: {
     'content_id': 10,
     'groundtruth': 3.33,
     'path': dataset_dir + '/dis/Session4/P02S09C1R3.yuv',
    },
    84: {
     'content_id': 10,
     'groundtruth': 0.83,
     'path': dataset_dir + '/dis/Session4/P02S09C1R4.yuv',
    },

    85: {
     'content_id': 9,
     'groundtruth': 8.17,
     'path': dataset_dir + '/dis/Session4/P02S10C2R1.yuv',
    },
    86: {
     'content_id': 9,
     'groundtruth': 6.33,
     'path': dataset_dir + '/dis/Session4/P02S10C2R2.yuv',
    },
    87: {
     'content_id': 9,
     'groundtruth': 5.13,
     'path': dataset_dir + '/dis/Session4/P02S10C2R3.yuv',
    },
    88: {
     'content_id': 9,
     'groundtruth': 2.13,
     'path': dataset_dir + '/dis/Session4/P02S10C2R4.yuv',
    },

    89: {
     'content_id': 7,
     'groundtruth': 8.42,
     'path': dataset_dir + '/dis/Session4/P02S11C2R1.yuv',
    },
    90: {
     'content_id': 7,
     'groundtruth': 7.42,
     'path': dataset_dir + '/dis/Session4/P02S11C2R2.yuv',
    },
    91: {
     'content_id': 7,
     'groundtruth': 5.54,
     'path': dataset_dir + '/dis/Session4/P02S11C2R3.yuv',
    },
    92: {
     'content_id': 7,
     'groundtruth': 3.04,
     'path': dataset_dir + '/dis/Session4/P02S11C2R4.yuv',
    },

    93: {
     'content_id': 8,
     'groundtruth': 8.83,
     'path': dataset_dir + '/dis/Session4/P02S12C3R1.yuv',
    },
    94: {
     'content_id': 8,
     'groundtruth': 7.67,
     'path': dataset_dir + '/dis/Session4/P02S12C3R2.yuv',
    },
    95: {
     'content_id': 8,
     'groundtruth': 3.67,
     'path': dataset_dir + '/dis/Session4/P02S12C3R3.yuv',
    },
    96: {
     'content_id': 8,
     'groundtruth': 0.21,
     'path': dataset_dir + '/dis/Session4/P02S12C3R4.yuv',
    },
}

# # downscale session3 from 4K to 1080
# for dis_video in dis_videos_session3:
#      dis_video['resampling_type'] = 'bicubic'
#      dis_video['quality_width'] = 1920
#      dis_video['quality_height'] = 1080

# dis_videos = dis_videos_session1 + dis_videos_session2 + dis_videos_session3 + dis_videos_session4
dis_videos = {}
dis_videos.update(dis_videos_session1)
dis_videos.update(dis_videos_session2)
dis_videos.update(dis_videos_session4)
