(() => {
  'use strict';

  const W = typeof window !== 'undefined'
    ? window
    : globalThis;
  const Lab = W.SCLab = W.SCLab || {};
  const VERSION = '0.23.0';
  const ROOT_SELECTOR =
    '[data-biomedical-biosignals-root]';
  const CATALOG = {"schema":"sc-lab-biomedical-engineering-biosignals-contract/1.0","version":"0.23.0","title":"Biomedical Engineering and Biosignals","categories":[{"id":"acquisition-sampling","label":"Acquisition and Sampling","description":"Sampling, duration, resolution, and quantization calculations."},{"id":"ecg-cardiac","label":"ECG and Cardiac Intervals","description":"Rate, interval correction, axis, and heart-rate variability calculations."},{"id":"ppg-hemodynamics","label":"PPG and Hemodynamics","description":"Pulse, perfusion, oxygenation approximation, transit, and waveform calculations."},{"id":"respiration","label":"Respiration","description":"Breathing rate, ventilation, timing, burden, and integrated-flow calculations."},{"id":"emg","label":"Electromyography","description":"Amplitude, activity, waveform, crossing, and shape features."},{"id":"eeg","label":"Electroencephalography","description":"Band power, spectral ratios, centroid, entropy, dominance, and asymmetry."},{"id":"filtering","label":"Filtering and Signal Conditioning","description":"Analog cutoff, moving-average, and exponential-smoothing parameters."},{"id":"signal-quality","label":"Signal Quality","description":"Noise, completeness, clipping, correlation, and composite quality checks."}],"methods":[{"id":"sampling-interval-ms","label":"Sampling interval","category":"acquisition-sampling","operation":"sampling_interval_ms","inputs":[{"key":"sampleRateHz","label":"Sample rate","unit":"Hz","type":"number","min":1e-06}],"output":{"unit":"ms"},"formula":"Δt = 1000 / fs","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"nyquist-frequency","label":"Nyquist frequency","category":"acquisition-sampling","operation":"nyquist_frequency","inputs":[{"key":"sampleRateHz","label":"Sample rate","unit":"Hz","type":"number","min":1e-06}],"output":{"unit":"Hz"},"formula":"fN = fs / 2","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"sample-count","label":"Sample count","category":"acquisition-sampling","operation":"sample_count","inputs":[{"key":"durationSeconds","label":"Duration","unit":"s","type":"number","min":0},{"key":"sampleRateHz","label":"Sample rate","unit":"Hz","type":"number","min":1e-06}],"output":{"unit":"samples"},"formula":"N = round(t × fs)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"duration-from-samples","label":"Duration from samples","category":"acquisition-sampling","operation":"duration_from_samples","inputs":[{"key":"sampleCount","label":"Sample count","unit":"samples","type":"integer","min":0},{"key":"sampleRateHz","label":"Sample rate","unit":"Hz","type":"number","min":1e-06}],"output":{"unit":"s"},"formula":"t = N / fs","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"adc-levels","label":"ADC levels","category":"acquisition-sampling","operation":"adc_levels","inputs":[{"key":"bits","label":"ADC resolution","unit":"bits","type":"integer","min":1,"max":32}],"output":{"unit":"levels"},"formula":"levels = 2^bits","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"quantization-step","label":"Quantization step","category":"acquisition-sampling","operation":"quantization_step","inputs":[{"key":"inputRange","label":"Full-scale input range","unit":"V","type":"number","min":1e-06},{"key":"bits","label":"ADC resolution","unit":"bits","type":"integer","min":1,"max":32}],"output":{"unit":"V/level"},"formula":"q = range / (2^bits − 1)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"heart-rate-from-rr","label":"Heart rate from RR","category":"ecg-cardiac","operation":"heart_rate_from_rr","inputs":[{"key":"rrSeconds","label":"RR interval","unit":"s","type":"number","min":1e-06}],"output":{"unit":"bpm"},"formula":"HR = 60 / RR","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"rr-from-heart-rate","label":"RR interval from heart rate","category":"ecg-cardiac","operation":"rr_from_heart_rate","inputs":[{"key":"heartRateBpm","label":"Heart rate","unit":"bpm","type":"number","min":1e-06}],"output":{"unit":"s"},"formula":"RR = 60 / HR","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"qtc-bazett","label":"QTc using Bazett","category":"ecg-cardiac","operation":"qtc_bazett","inputs":[{"key":"qtSeconds","label":"QT interval","unit":"s","type":"number","min":0},{"key":"rrSeconds","label":"RR interval","unit":"s","type":"number","min":1e-06}],"output":{"unit":"s"},"formula":"QTc = QT / √RR","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"qtc-fridericia","label":"QTc using Fridericia","category":"ecg-cardiac","operation":"qtc_fridericia","inputs":[{"key":"qtSeconds","label":"QT interval","unit":"s","type":"number","min":0},{"key":"rrSeconds","label":"RR interval","unit":"s","type":"number","min":1e-06}],"output":{"unit":"s"},"formula":"QTc = QT / RR^(1/3)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"ecg-axis-angle","label":"ECG vector angle","category":"ecg-cardiac","operation":"ecg_axis_angle","inputs":[{"key":"xComponent","label":"Horizontal component","unit":"mV","type":"number"},{"key":"yComponent","label":"Vertical component","unit":"mV","type":"number"}],"output":{"unit":"degrees"},"formula":"θ = atan2(y, x)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"hrv-rmssd","label":"HRV RMSSD","category":"ecg-cardiac","operation":"hrv_rmssd","inputs":[{"key":"rrIntervalsMs","label":"RR intervals","unit":"ms","type":"array","minItems":2}],"output":{"unit":"ms"},"formula":"RMSSD = √mean(ΔRR²)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"hrv-sdnn","label":"HRV SDNN","category":"ecg-cardiac","operation":"hrv_sdnn","inputs":[{"key":"rrIntervalsMs","label":"RR intervals","unit":"ms","type":"array","minItems":2}],"output":{"unit":"ms"},"formula":"SDNN = sample SD(RR)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"pulse-rate-from-interval","label":"Pulse rate from interval","category":"ppg-hemodynamics","operation":"pulse_rate_from_interval","inputs":[{"key":"pulseIntervalSeconds","label":"Pulse interval","unit":"s","type":"number","min":1e-06}],"output":{"unit":"bpm"},"formula":"PR = 60 / interval","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"perfusion-index","label":"Perfusion index","category":"ppg-hemodynamics","operation":"perfusion_index","inputs":[{"key":"acAmplitude","label":"AC amplitude","unit":"a.u.","type":"number","min":0},{"key":"dcLevel","label":"DC level","unit":"a.u.","type":"number","min":1e-06}],"output":{"unit":"%"},"formula":"PI = AC / DC × 100","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"spo2-ratio-estimate","label":"SpO₂ ratio estimate","category":"ppg-hemodynamics","operation":"spo2_ratio_estimate","inputs":[{"key":"acRed","label":"Red AC","unit":"a.u.","type":"number","min":0},{"key":"dcRed","label":"Red DC","unit":"a.u.","type":"number","min":1e-06},{"key":"acInfrared","label":"Infrared AC","unit":"a.u.","type":"number","min":0},{"key":"dcInfrared","label":"Infrared DC","unit":"a.u.","type":"number","min":1e-06}],"output":{"unit":"%"},"formula":"estimate = clamp(110 − 25R, 0, 100)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"pulse-transit-time","label":"Pulse transit time","category":"ppg-hemodynamics","operation":"pulse_transit_time","inputs":[{"key":"proximalTimeSeconds","label":"Proximal event time","unit":"s","type":"number"},{"key":"distalTimeSeconds","label":"Distal event time","unit":"s","type":"number"}],"output":{"unit":"s"},"formula":"PTT = tdistal − tproximal","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"pulse-wave-velocity","label":"Pulse wave velocity","category":"ppg-hemodynamics","operation":"pulse_wave_velocity","inputs":[{"key":"distanceMeters","label":"Path distance","unit":"m","type":"number","min":0},{"key":"transitTimeSeconds","label":"Transit time","unit":"s","type":"number","min":1e-06}],"output":{"unit":"m/s"},"formula":"PWV = distance / transit time","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"respiratory-rate","label":"Respiratory rate","category":"respiration","operation":"respiratory_rate","inputs":[{"key":"breathIntervalSeconds","label":"Breath interval","unit":"s","type":"number","min":1e-06}],"output":{"unit":"breaths/min"},"formula":"RR = 60 / interval","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"minute-ventilation","label":"Minute ventilation","category":"respiration","operation":"minute_ventilation","inputs":[{"key":"tidalVolumeLiters","label":"Tidal volume","unit":"L","type":"number","min":0},{"key":"respiratoryRate","label":"Respiratory rate","unit":"breaths/min","type":"number","min":0}],"output":{"unit":"L/min"},"formula":"VE = VT × RR","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"inspiratory-expiratory-ratio","label":"Inspiratory-to-expiratory ratio","category":"respiration","operation":"ie_ratio","inputs":[{"key":"inspirationSeconds","label":"Inspiratory time","unit":"s","type":"number","min":0},{"key":"expirationSeconds","label":"Expiratory time","unit":"s","type":"number","min":1e-06}],"output":{"unit":"ratio"},"formula":"I:E = Ti / Te","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"inspiratory-duty-cycle","label":"Inspiratory duty cycle","category":"respiration","operation":"inspiratory_duty_cycle","inputs":[{"key":"inspirationSeconds","label":"Inspiratory time","unit":"s","type":"number","min":0},{"key":"expirationSeconds","label":"Expiratory time","unit":"s","type":"number","min":0}],"output":{"unit":"%"},"formula":"duty = Ti / (Ti + Te) × 100","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"apnea-burden","label":"Apnea burden","category":"respiration","operation":"apnea_burden","inputs":[{"key":"apneaSeconds","label":"Total apnea time","unit":"s","type":"number","min":0},{"key":"recordingSeconds","label":"Recording duration","unit":"s","type":"number","min":1e-06}],"output":{"unit":"%"},"formula":"burden = apnea time / recording time × 100","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"integrated-respiratory-volume","label":"Integrated respiratory volume","category":"respiration","operation":"integrated_respiratory_volume","inputs":[{"key":"meanFlowLitersPerSecond","label":"Mean flow","unit":"L/s","type":"number"},{"key":"durationSeconds","label":"Duration","unit":"s","type":"number","min":0}],"output":{"unit":"L"},"formula":"volume = mean flow × duration","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"emg-rms","label":"EMG RMS","category":"emg","operation":"emg_rms","inputs":[{"key":"samples","label":"EMG samples","unit":"a.u.","type":"array","minItems":1}],"output":{"unit":"a.u."},"formula":"RMS = √mean(x²)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"emg-mean-absolute-value","label":"EMG mean absolute value","category":"emg","operation":"emg_mav","inputs":[{"key":"samples","label":"EMG samples","unit":"a.u.","type":"array","minItems":1}],"output":{"unit":"a.u."},"formula":"MAV = mean(|x|)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"integrated-emg","label":"Integrated EMG","category":"emg","operation":"integrated_emg","inputs":[{"key":"samples","label":"EMG samples","unit":"a.u.","type":"array","minItems":1},{"key":"sampleIntervalSeconds","label":"Sample interval","unit":"s","type":"number","min":0}],"output":{"unit":"a.u.·s"},"formula":"IEMG = Σ|x| × Δt","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"emg-waveform-length","label":"EMG waveform length","category":"emg","operation":"emg_waveform_length","inputs":[{"key":"samples","label":"EMG samples","unit":"a.u.","type":"array","minItems":2}],"output":{"unit":"a.u."},"formula":"WL = Σ|xi − xi−1|","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"zero-crossing-rate","label":"Zero-crossing rate","category":"emg","operation":"zero_crossing_rate","inputs":[{"key":"samples","label":"Signal samples","unit":"a.u.","type":"array","minItems":2},{"key":"sampleRateHz","label":"Sample rate","unit":"Hz","type":"number","min":1e-06}],"output":{"unit":"crossings/s"},"formula":"ZCR = crossings / (N − 1) × fs","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"peak-to-peak-amplitude","label":"Peak-to-peak amplitude","category":"emg","operation":"peak_to_peak","inputs":[{"key":"samples","label":"Signal samples","unit":"a.u.","type":"array","minItems":1}],"output":{"unit":"a.u."},"formula":"P2P = max(x) − min(x)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"crest-factor","label":"Crest factor","category":"emg","operation":"crest_factor","inputs":[{"key":"samples","label":"Signal samples","unit":"a.u.","type":"array","minItems":1}],"output":{"unit":"ratio"},"formula":"CF = max(|x|) / RMS","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"absolute-band-power","label":"Absolute band power","category":"eeg","operation":"absolute_band_power","inputs":[{"key":"frequenciesHz","label":"Frequency bins","unit":"Hz","type":"array","minItems":1},{"key":"powerValues","label":"Power values","unit":"a.u.","type":"array","minItems":1},{"key":"lowHz","label":"Band low","unit":"Hz","type":"number","min":0},{"key":"highHz","label":"Band high","unit":"Hz","type":"number","min":0},{"key":"binWidthHz","label":"Bin width","unit":"Hz","type":"number","min":1e-06}],"output":{"unit":"a.u.·Hz"},"formula":"Pband = ΣP(f in band) × Δf","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"relative-band-power","label":"Relative band power","category":"eeg","operation":"relative_band_power","inputs":[{"key":"bandPower","label":"Band power","unit":"a.u.","type":"number","min":0},{"key":"totalPower","label":"Total power","unit":"a.u.","type":"number","min":1e-06}],"output":{"unit":"%"},"formula":"relative power = band / total × 100","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"alpha-beta-ratio","label":"Alpha-to-beta ratio","category":"eeg","operation":"alpha_beta_ratio","inputs":[{"key":"alphaPower","label":"Alpha power","unit":"a.u.","type":"number","min":0},{"key":"betaPower","label":"Beta power","unit":"a.u.","type":"number","min":1e-06}],"output":{"unit":"ratio"},"formula":"ratio = alpha / beta","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"theta-beta-ratio","label":"Theta-to-beta ratio","category":"eeg","operation":"theta_beta_ratio","inputs":[{"key":"thetaPower","label":"Theta power","unit":"a.u.","type":"number","min":0},{"key":"betaPower","label":"Beta power","unit":"a.u.","type":"number","min":1e-06}],"output":{"unit":"ratio"},"formula":"ratio = theta / beta","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"spectral-centroid","label":"Spectral centroid","category":"eeg","operation":"spectral_centroid","inputs":[{"key":"frequenciesHz","label":"Frequency bins","unit":"Hz","type":"array","minItems":1},{"key":"powerValues","label":"Power values","unit":"a.u.","type":"array","minItems":1}],"output":{"unit":"Hz"},"formula":"centroid = Σ(fP) / ΣP","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"spectral-entropy","label":"Normalized spectral entropy","category":"eeg","operation":"spectral_entropy","inputs":[{"key":"powerValues","label":"Power values","unit":"a.u.","type":"array","minItems":2}],"output":{"unit":"0–1"},"formula":"H = −Σpi log2(pi) / log2(N)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"dominant-frequency","label":"Dominant frequency","category":"eeg","operation":"dominant_frequency","inputs":[{"key":"frequenciesHz","label":"Frequency bins","unit":"Hz","type":"array","minItems":1},{"key":"powerValues","label":"Power values","unit":"a.u.","type":"array","minItems":1}],"output":{"unit":"Hz"},"formula":"fd = frequency at maximum power","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"hemispheric-asymmetry","label":"Hemispheric asymmetry","category":"eeg","operation":"hemispheric_asymmetry","inputs":[{"key":"leftPower","label":"Left power","unit":"a.u.","type":"number","min":0},{"key":"rightPower","label":"Right power","unit":"a.u.","type":"number","min":0}],"output":{"unit":"%"},"formula":"asymmetry = (R − L) / (R + L) × 100","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"rc-low-pass-cutoff","label":"RC low-pass cutoff","category":"filtering","operation":"rc_cutoff","inputs":[{"key":"resistanceOhms","label":"Resistance","unit":"Ω","type":"number","min":1e-06},{"key":"capacitanceFarads","label":"Capacitance","unit":"F","type":"number","min":1e-12}],"output":{"unit":"Hz"},"formula":"fc = 1 / (2πRC)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"rc-high-pass-cutoff","label":"RC high-pass cutoff","category":"filtering","operation":"rc_cutoff","inputs":[{"key":"resistanceOhms","label":"Resistance","unit":"Ω","type":"number","min":1e-06},{"key":"capacitanceFarads","label":"Capacitance","unit":"F","type":"number","min":1e-12}],"output":{"unit":"Hz"},"formula":"fc = 1 / (2πRC)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"moving-average-latest","label":"Latest moving average","category":"filtering","operation":"moving_average_latest","inputs":[{"key":"samples","label":"Signal samples","unit":"a.u.","type":"array","minItems":1},{"key":"windowSize","label":"Window size","unit":"samples","type":"integer","min":1}],"output":{"unit":"a.u."},"formula":"MA = mean(last W samples)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"exponential-smoothing-alpha","label":"Exponential smoothing alpha","category":"filtering","operation":"exponential_smoothing_alpha","inputs":[{"key":"sampleIntervalSeconds","label":"Sample interval","unit":"s","type":"number","min":0},{"key":"timeConstantSeconds","label":"Time constant","unit":"s","type":"number","min":1e-06}],"output":{"unit":"0–1"},"formula":"α = Δt / (τ + Δt)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"snr-db","label":"Signal-to-noise ratio","category":"signal-quality","operation":"snr_db","inputs":[{"key":"signalRms","label":"Signal RMS","unit":"a.u.","type":"number","min":1e-06},{"key":"noiseRms","label":"Noise RMS","unit":"a.u.","type":"number","min":1e-06}],"output":{"unit":"dB"},"formula":"SNR = 20 log10(signal/noise)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"missing-sample-percent","label":"Missing sample percentage","category":"signal-quality","operation":"missing_sample_percent","inputs":[{"key":"missingCount","label":"Missing samples","unit":"samples","type":"integer","min":0},{"key":"totalCount","label":"Total samples","unit":"samples","type":"integer","min":1}],"output":{"unit":"%"},"formula":"missing = missing / total × 100","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"clipping-percent","label":"Clipping percentage","category":"signal-quality","operation":"clipping_percent","inputs":[{"key":"clippedCount","label":"Clipped samples","unit":"samples","type":"integer","min":0},{"key":"totalCount","label":"Total samples","unit":"samples","type":"integer","min":1}],"output":{"unit":"%"},"formula":"clipping = clipped / total × 100","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"pearson-correlation","label":"Pearson correlation","category":"signal-quality","operation":"pearson_correlation","inputs":[{"key":"xValues","label":"Reference samples","unit":"a.u.","type":"array","minItems":2},{"key":"yValues","label":"Comparison samples","unit":"a.u.","type":"array","minItems":2}],"output":{"unit":"r"},"formula":"r = cov(x,y) / (SDx SDy)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."},{"id":"signal-quality-index","label":"Composite signal quality index","category":"signal-quality","operation":"signal_quality_index","inputs":[{"key":"snrDb","label":"SNR","unit":"dB","type":"number"},{"key":"missingPercent","label":"Missing samples","unit":"%","type":"number","min":0},{"key":"clippingPercent","label":"Clipping","unit":"%","type":"number","min":0}],"output":{"unit":"0–100"},"formula":"SQI = clamp(50 + 2·SNR − 2·missing − 3·clipping, 0, 100)","responsibleUse":"Research and education only; not a diagnostic or clinical decision."}],"benchmarks":[{"id":"benchmark-sampling-interval-ms","methodId":"sampling-interval-ms","inputs":{"sampleRateHz":250},"expected":4.0,"tolerance":4e-09},{"id":"benchmark-nyquist-frequency","methodId":"nyquist-frequency","inputs":{"sampleRateHz":500},"expected":250.0,"tolerance":2.5000000000000004e-07},{"id":"benchmark-sample-count","methodId":"sample-count","inputs":{"durationSeconds":10,"sampleRateHz":250},"expected":2500.0,"tolerance":2.5e-06},{"id":"benchmark-duration-from-samples","methodId":"duration-from-samples","inputs":{"sampleCount":1250,"sampleRateHz":250},"expected":5.0,"tolerance":5e-09},{"id":"benchmark-adc-levels","methodId":"adc-levels","inputs":{"bits":12},"expected":4096.0,"tolerance":4.096e-06},{"id":"benchmark-quantization-step","methodId":"quantization-step","inputs":{"inputRange":3.3,"bits":12},"expected":0.0008058608058608059,"tolerance":1e-09},{"id":"benchmark-heart-rate-from-rr","methodId":"heart-rate-from-rr","inputs":{"rrSeconds":0.8},"expected":75.0,"tolerance":7.500000000000001e-08},{"id":"benchmark-rr-from-heart-rate","methodId":"rr-from-heart-rate","inputs":{"heartRateBpm":75},"expected":0.8,"tolerance":1e-09},{"id":"benchmark-qtc-bazett","methodId":"qtc-bazett","inputs":{"qtSeconds":0.36,"rrSeconds":0.81},"expected":0.39999999999999997,"tolerance":1e-09},{"id":"benchmark-qtc-fridericia","methodId":"qtc-fridericia","inputs":{"qtSeconds":0.36,"rrSeconds":0.729},"expected":0.39999999999999997,"tolerance":1e-09},{"id":"benchmark-ecg-axis-angle","methodId":"ecg-axis-angle","inputs":{"xComponent":1,"yComponent":1},"expected":45.0,"tolerance":4.5000000000000006e-08},{"id":"benchmark-hrv-rmssd","methodId":"hrv-rmssd","inputs":{"rrIntervalsMs":[800,810,790,805]},"expected":15.545631755148024,"tolerance":1.5545631755148025e-08},{"id":"benchmark-hrv-sdnn","methodId":"hrv-sdnn","inputs":{"rrIntervalsMs":[800,810,790,805]},"expected":8.539125638299666,"tolerance":8.539125638299667e-09},{"id":"benchmark-pulse-rate-from-interval","methodId":"pulse-rate-from-interval","inputs":{"pulseIntervalSeconds":0.75},"expected":80.0,"tolerance":8e-08},{"id":"benchmark-perfusion-index","methodId":"perfusion-index","inputs":{"acAmplitude":2,"dcLevel":100},"expected":2.0,"tolerance":2e-09},{"id":"benchmark-spo2-ratio-estimate","methodId":"spo2-ratio-estimate","inputs":{"acRed":0.5,"dcRed":10,"acInfrared":1,"dcInfrared":10},"expected":97.5,"tolerance":9.75e-08},{"id":"benchmark-pulse-transit-time","methodId":"pulse-transit-time","inputs":{"proximalTimeSeconds":1.1,"distalTimeSeconds":1.35},"expected":0.25,"tolerance":1e-09},{"id":"benchmark-pulse-wave-velocity","methodId":"pulse-wave-velocity","inputs":{"distanceMeters":0.5,"transitTimeSeconds":0.1},"expected":5.0,"tolerance":5e-09},{"id":"benchmark-respiratory-rate","methodId":"respiratory-rate","inputs":{"breathIntervalSeconds":4},"expected":15.0,"tolerance":1.5000000000000002e-08},{"id":"benchmark-minute-ventilation","methodId":"minute-ventilation","inputs":{"tidalVolumeLiters":0.5,"respiratoryRate":12},"expected":6.0,"tolerance":6.000000000000001e-09},{"id":"benchmark-inspiratory-expiratory-ratio","methodId":"inspiratory-expiratory-ratio","inputs":{"inspirationSeconds":2,"expirationSeconds":3},"expected":0.6666666666666666,"tolerance":1e-09},{"id":"benchmark-inspiratory-duty-cycle","methodId":"inspiratory-duty-cycle","inputs":{"inspirationSeconds":2,"expirationSeconds":3},"expected":40.0,"tolerance":4e-08},{"id":"benchmark-apnea-burden","methodId":"apnea-burden","inputs":{"apneaSeconds":60,"recordingSeconds":3600},"expected":1.6666666666666667,"tolerance":1.666666666666667e-09},{"id":"benchmark-integrated-respiratory-volume","methodId":"integrated-respiratory-volume","inputs":{"meanFlowLitersPerSecond":0.4,"durationSeconds":2},"expected":0.8,"tolerance":1e-09},{"id":"benchmark-emg-rms","methodId":"emg-rms","inputs":{"samples":[1,-1,1,-1]},"expected":1.0,"tolerance":1e-09},{"id":"benchmark-emg-mean-absolute-value","methodId":"emg-mean-absolute-value","inputs":{"samples":[1,-2,3,-4]},"expected":2.5,"tolerance":2.5e-09},{"id":"benchmark-integrated-emg","methodId":"integrated-emg","inputs":{"samples":[1,-2,3],"sampleIntervalSeconds":0.01},"expected":0.06,"tolerance":1e-09},{"id":"benchmark-emg-waveform-length","methodId":"emg-waveform-length","inputs":{"samples":[1,3,2,5]},"expected":6.0,"tolerance":6.000000000000001e-09},{"id":"benchmark-zero-crossing-rate","methodId":"zero-crossing-rate","inputs":{"samples":[-1,1,-1,1],"sampleRateHz":100},"expected":100.0,"tolerance":1.0000000000000001e-07},{"id":"benchmark-peak-to-peak-amplitude","methodId":"peak-to-peak-amplitude","inputs":{"samples":[-2,1,4,0]},"expected":6.0,"tolerance":6.000000000000001e-09},{"id":"benchmark-crest-factor","methodId":"crest-factor","inputs":{"samples":[0,3,4,0]},"expected":1.6,"tolerance":1.6000000000000003e-09},{"id":"benchmark-absolute-band-power","methodId":"absolute-band-power","inputs":{"frequenciesHz":[1,2,3,4],"powerValues":[1,2,3,4],"lowHz":2,"highHz":3,"binWidthHz":1},"expected":5.0,"tolerance":5e-09},{"id":"benchmark-relative-band-power","methodId":"relative-band-power","inputs":{"bandPower":25,"totalPower":100},"expected":25.0,"tolerance":2.5000000000000002e-08},{"id":"benchmark-alpha-beta-ratio","methodId":"alpha-beta-ratio","inputs":{"alphaPower":20,"betaPower":10},"expected":2.0,"tolerance":2e-09},{"id":"benchmark-theta-beta-ratio","methodId":"theta-beta-ratio","inputs":{"thetaPower":15,"betaPower":5},"expected":3.0,"tolerance":3.0000000000000004e-09},{"id":"benchmark-spectral-centroid","methodId":"spectral-centroid","inputs":{"frequenciesHz":[1,2,3],"powerValues":[1,2,1]},"expected":2.0,"tolerance":2e-09},{"id":"benchmark-spectral-entropy","methodId":"spectral-entropy","inputs":{"powerValues":[1,1,1,1]},"expected":1.0,"tolerance":1e-09},{"id":"benchmark-dominant-frequency","methodId":"dominant-frequency","inputs":{"frequenciesHz":[5,10,15],"powerValues":[1,4,2]},"expected":10.0,"tolerance":1e-08},{"id":"benchmark-hemispheric-asymmetry","methodId":"hemispheric-asymmetry","inputs":{"leftPower":40,"rightPower":60},"expected":20.0,"tolerance":2e-08},{"id":"benchmark-rc-low-pass-cutoff","methodId":"rc-low-pass-cutoff","inputs":{"resistanceOhms":1000,"capacitanceFarads":1e-06},"expected":159.15494309189535,"tolerance":1.5915494309189535e-07},{"id":"benchmark-rc-high-pass-cutoff","methodId":"rc-high-pass-cutoff","inputs":{"resistanceOhms":10000,"capacitanceFarads":1e-06},"expected":15.915494309189533,"tolerance":1.5915494309189534e-08},{"id":"benchmark-moving-average-latest","methodId":"moving-average-latest","inputs":{"samples":[1,2,3,4,5],"windowSize":3},"expected":4.0,"tolerance":4e-09},{"id":"benchmark-exponential-smoothing-alpha","methodId":"exponential-smoothing-alpha","inputs":{"sampleIntervalSeconds":0.1,"timeConstantSeconds":0.9},"expected":0.1,"tolerance":1e-09},{"id":"benchmark-snr-db","methodId":"snr-db","inputs":{"signalRms":10,"noiseRms":1},"expected":20.0,"tolerance":2e-08},{"id":"benchmark-missing-sample-percent","methodId":"missing-sample-percent","inputs":{"missingCount":5,"totalCount":100},"expected":5.0,"tolerance":5e-09},{"id":"benchmark-clipping-percent","methodId":"clipping-percent","inputs":{"clippedCount":2,"totalCount":100},"expected":2.0,"tolerance":2e-09},{"id":"benchmark-pearson-correlation","methodId":"pearson-correlation","inputs":{"xValues":[1,2,3,4],"yValues":[2,4,6,8]},"expected":1.0,"tolerance":1e-09},{"id":"benchmark-signal-quality-index","methodId":"signal-quality-index","inputs":{"snrDb":20,"missingPercent":2,"clippingPercent":1},"expected":83.0,"tolerance":8.3e-08}],"waveformAnalysis":{"features":["sampleCount","durationSeconds","mean","standardDeviation","rms","minimum","maximum","peakToPeak","zeroCrossingCount","zeroCrossingRate","crestFactor"]},"responsibleUse":{"scope":"Research, education, prototyping, and non-clinical signal analysis.","boundary":"Not for diagnosis, treatment, patient monitoring, alarm generation, or clinical decision-making."}};

  const state = {
    currentResult: null,
    waveformResult: null,
    batchResult: null,
    provenanceRecord: null,
    lastError: null,
    rendered: false,
  };

  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  function finite(value, label) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      throw new Error(`${label} must be numerical and finite.`);
    }

    return number;
  }

  function positive(value, label) {
    const number = finite(value, label);

    if (number <= 0) {
      throw new Error(`${label} must be greater than zero.`);
    }

    return number;
  }

  function values(value, label, minimum = 1) {
    let raw = value;

    if (typeof raw === 'string') {
      const trimmed = raw.trim();

      if (
        trimmed.startsWith('[')
        && trimmed.endsWith(']')
      ) {
        raw = JSON.parse(trimmed);
      } else {
        raw = trimmed
          .split(/[,\s]+/)
          .filter(Boolean);
      }
    }

    if (!Array.isArray(raw)) {
      throw new Error(`${label} must be an array.`);
    }

    const numbers = raw.map(
      (item, index) => finite(
        item,
        `${label}[${index}]`
      )
    );

    if (numbers.length < minimum) {
      throw new Error(
        `${label} requires at least ${minimum} values.`
      );
    }

    return numbers;
  }

  function mean(items) {
    return items.reduce(
      (sum, item) => sum + item,
      0
    ) / items.length;
  }

  function standardDeviation(items) {
    if (items.length < 2) {
      return 0;
    }

    const average = mean(items);

    return Math.sqrt(
      items.reduce(
        (sum, item) => (
          sum + (item - average) ** 2
        ),
        0
      ) / (items.length - 1)
    );
  }

  function rms(items) {
    return Math.sqrt(
      mean(
        items.map(
          (item) => item * item
        )
      )
    );
  }

  function paired(
    left,
    right,
    leftLabel,
    rightLabel
  ) {
    const a = values(left, leftLabel);
    const b = values(right, rightLabel);

    if (a.length !== b.length) {
      throw new Error(
        `${leftLabel} and ${rightLabel} must have equal length.`
      );
    }

    return [a, b];
  }

  function method(methodId) {
    return CATALOG.methods.find(
      (item) => item.id === methodId
    ) || null;
  }

  function execute(methodId, inputs = {}) {
    const definition = method(methodId);

    if (!definition) {
      throw new Error(
        `Unknown biosignal method: ${methodId}`
      );
    }

    const operation = definition.operation;
    const i = inputs;
    let result;

    switch (operation) {
      case 'sampling_interval_ms':
        result = 1000 / positive(
          i.sampleRateHz,
          'sampleRateHz'
        );
        break;
      case 'nyquist_frequency':
        result = positive(
          i.sampleRateHz,
          'sampleRateHz'
        ) / 2;
        break;
      case 'sample_count':
        result = Math.round(
          finite(
            i.durationSeconds,
            'durationSeconds'
          )
          * positive(
            i.sampleRateHz,
            'sampleRateHz'
          )
        );
        break;
      case 'duration_from_samples':
        result = finite(
          i.sampleCount,
          'sampleCount'
        ) / positive(
          i.sampleRateHz,
          'sampleRateHz'
        );
        break;
      case 'adc_levels': {
        const bits = Math.trunc(
          positive(i.bits, 'bits')
        );
        result = 2 ** bits;
        break;
      }
      case 'quantization_step': {
        const bits = Math.trunc(
          positive(i.bits, 'bits')
        );
        result = positive(
          i.inputRange,
          'inputRange'
        ) / ((2 ** bits) - 1);
        break;
      }
      case 'heart_rate_from_rr':
        result = 60 / positive(
          i.rrSeconds,
          'rrSeconds'
        );
        break;
      case 'rr_from_heart_rate':
        result = 60 / positive(
          i.heartRateBpm,
          'heartRateBpm'
        );
        break;
      case 'qtc_bazett':
        result = finite(
          i.qtSeconds,
          'qtSeconds'
        ) / Math.sqrt(
          positive(
            i.rrSeconds,
            'rrSeconds'
          )
        );
        break;
      case 'qtc_fridericia':
        result = finite(
          i.qtSeconds,
          'qtSeconds'
        ) / (
          positive(
            i.rrSeconds,
            'rrSeconds'
          ) ** (1 / 3)
        );
        break;
      case 'ecg_axis_angle':
        result = Math.atan2(
          finite(i.yComponent, 'yComponent'),
          finite(i.xComponent, 'xComponent')
        ) * 180 / Math.PI;
        break;
      case 'hrv_rmssd': {
        const samples = values(
          i.rrIntervalsMs,
          'rrIntervalsMs',
          2
        );
        const differences = samples
          .slice(1)
          .map(
            (value, index) => (
              value - samples[index]
            )
          );
        result = Math.sqrt(
          mean(
            differences.map(
              (difference) => (
                difference * difference
              )
            )
          )
        );
        break;
      }
      case 'hrv_sdnn':
        result = standardDeviation(
          values(
            i.rrIntervalsMs,
            'rrIntervalsMs',
            2
          )
        );
        break;
      case 'pulse_rate_from_interval':
        result = 60 / positive(
          i.pulseIntervalSeconds,
          'pulseIntervalSeconds'
        );
        break;
      case 'perfusion_index':
        result = finite(
          i.acAmplitude,
          'acAmplitude'
        ) / positive(
          i.dcLevel,
          'dcLevel'
        ) * 100;
        break;
      case 'spo2_ratio_estimate': {
        const ratio = (
          finite(i.acRed, 'acRed')
          / positive(i.dcRed, 'dcRed')
        ) / (
          positive(
            i.acInfrared,
            'acInfrared'
          )
          / positive(
            i.dcInfrared,
            'dcInfrared'
          )
        );
        result = Math.max(
          0,
          Math.min(
            100,
            110 - 25 * ratio
          )
        );
        break;
      }
      case 'pulse_transit_time':
        result = finite(
          i.distalTimeSeconds,
          'distalTimeSeconds'
        ) - finite(
          i.proximalTimeSeconds,
          'proximalTimeSeconds'
        );
        break;
      case 'pulse_wave_velocity':
        result = finite(
          i.distanceMeters,
          'distanceMeters'
        ) / positive(
          i.transitTimeSeconds,
          'transitTimeSeconds'
        );
        break;
      case 'respiratory_rate':
        result = 60 / positive(
          i.breathIntervalSeconds,
          'breathIntervalSeconds'
        );
        break;
      case 'minute_ventilation':
        result = finite(
          i.tidalVolumeLiters,
          'tidalVolumeLiters'
        ) * finite(
          i.respiratoryRate,
          'respiratoryRate'
        );
        break;
      case 'ie_ratio':
        result = finite(
          i.inspirationSeconds,
          'inspirationSeconds'
        ) / positive(
          i.expirationSeconds,
          'expirationSeconds'
        );
        break;
      case 'inspiratory_duty_cycle': {
        const inspiration = finite(
          i.inspirationSeconds,
          'inspirationSeconds'
        );
        const expiration = finite(
          i.expirationSeconds,
          'expirationSeconds'
        );
        const duration = inspiration + expiration;

        if (duration <= 0) {
          throw new Error(
            'The respiratory cycle duration must be greater than zero.'
          );
        }

        result = inspiration / duration * 100;
        break;
      }
      case 'apnea_burden':
        result = finite(
          i.apneaSeconds,
          'apneaSeconds'
        ) / positive(
          i.recordingSeconds,
          'recordingSeconds'
        ) * 100;
        break;
      case 'integrated_respiratory_volume':
        result = finite(
          i.meanFlowLitersPerSecond,
          'meanFlowLitersPerSecond'
        ) * finite(
          i.durationSeconds,
          'durationSeconds'
        );
        break;
      case 'emg_rms':
        result = rms(
          values(i.samples, 'samples')
        );
        break;
      case 'emg_mav':
        result = mean(
          values(i.samples, 'samples')
            .map(Math.abs)
        );
        break;
      case 'integrated_emg':
        result = values(
          i.samples,
          'samples'
        ).reduce(
          (sum, value) => sum + Math.abs(value),
          0
        ) * finite(
          i.sampleIntervalSeconds,
          'sampleIntervalSeconds'
        );
        break;
      case 'emg_waveform_length': {
        const samples = values(
          i.samples,
          'samples',
          2
        );
        result = samples
          .slice(1)
          .reduce(
            (sum, value, index) => (
              sum
              + Math.abs(
                value - samples[index]
              )
            ),
            0
          );
        break;
      }
      case 'zero_crossing_rate': {
        const samples = values(
          i.samples,
          'samples',
          2
        );
        let crossings = 0;

        for (
          let index = 1;
          index < samples.length;
          index += 1
        ) {
          if (
            (
              samples[index - 1] < 0
              && samples[index] >= 0
            )
            || (
              samples[index - 1] >= 0
              && samples[index] < 0
            )
          ) {
            crossings += 1;
          }
        }

        result = (
          crossings
          / (samples.length - 1)
          * positive(
            i.sampleRateHz,
            'sampleRateHz'
          )
        );
        break;
      }
      case 'peak_to_peak': {
        const samples = values(
          i.samples,
          'samples'
        );
        result = Math.max(...samples)
          - Math.min(...samples);
        break;
      }
      case 'crest_factor': {
        const samples = values(
          i.samples,
          'samples'
        );
        const rootMeanSquare = rms(samples);
        result = rootMeanSquare
          ? Math.max(
              ...samples.map(Math.abs)
            ) / rootMeanSquare
          : 0;
        break;
      }
      case 'absolute_band_power': {
        const [frequencies, powers] = paired(
          i.frequenciesHz,
          i.powerValues,
          'frequenciesHz',
          'powerValues'
        );
        const low = finite(i.lowHz, 'lowHz');
        const high = finite(i.highHz, 'highHz');
        const width = positive(
          i.binWidthHz,
          'binWidthHz'
        );
        result = powers.reduce(
          (sum, power, index) => (
            frequencies[index] >= low
            && frequencies[index] <= high
              ? sum + power
              : sum
          ),
          0
        ) * width;
        break;
      }
      case 'relative_band_power':
        result = finite(
          i.bandPower,
          'bandPower'
        ) / positive(
          i.totalPower,
          'totalPower'
        ) * 100;
        break;
      case 'alpha_beta_ratio':
        result = finite(
          i.alphaPower,
          'alphaPower'
        ) / positive(
          i.betaPower,
          'betaPower'
        );
        break;
      case 'theta_beta_ratio':
        result = finite(
          i.thetaPower,
          'thetaPower'
        ) / positive(
          i.betaPower,
          'betaPower'
        );
        break;
      case 'spectral_centroid': {
        const [frequencies, powers] = paired(
          i.frequenciesHz,
          i.powerValues,
          'frequenciesHz',
          'powerValues'
        );
        const total = powers.reduce(
          (sum, power) => sum + power,
          0
        );

        if (total <= 0) {
          throw new Error(
            'powerValues must contain positive total power.'
          );
        }

        result = powers.reduce(
          (sum, power, index) => (
            sum + frequencies[index] * power
          ),
          0
        ) / total;
        break;
      }
      case 'spectral_entropy': {
        const powers = values(
          i.powerValues,
          'powerValues',
          2
        );
        const total = powers.reduce(
          (sum, power) => sum + power,
          0
        );

        if (total <= 0) {
          throw new Error(
            'powerValues must contain positive total power.'
          );
        }

        const entropy = powers.reduce(
          (sum, power) => {
            if (power <= 0) {
              return sum;
            }

            const probability = power / total;

            return sum
              - probability * Math.log2(probability);
          },
          0
        );
        result = entropy / Math.log2(powers.length);
        break;
      }
      case 'dominant_frequency': {
        const [frequencies, powers] = paired(
          i.frequenciesHz,
          i.powerValues,
          'frequenciesHz',
          'powerValues'
        );
        const index = powers.reduce(
          (best, power, current) => (
            power > powers[best]
              ? current
              : best
          ),
          0
        );
        result = frequencies[index];
        break;
      }
      case 'hemispheric_asymmetry': {
        const left = finite(
          i.leftPower,
          'leftPower'
        );
        const right = finite(
          i.rightPower,
          'rightPower'
        );
        const denominator = right + left;

        if (denominator === 0) {
          throw new Error(
            'leftPower and rightPower cannot both be zero.'
          );
        }

        result = (
          (right - left)
          / denominator
          * 100
        );
        break;
      }
      case 'rc_cutoff':
        result = 1 / (
          2
          * Math.PI
          * positive(
            i.resistanceOhms,
            'resistanceOhms'
          )
          * positive(
            i.capacitanceFarads,
            'capacitanceFarads'
          )
        );
        break;
      case 'moving_average_latest': {
        const samples = values(
          i.samples,
          'samples'
        );
        const windowSize = Math.trunc(
          positive(
            i.windowSize,
            'windowSize'
          )
        );

        if (windowSize > samples.length) {
          throw new Error(
            'windowSize cannot exceed the sample count.'
          );
        }

        result = mean(
          samples.slice(-windowSize)
        );
        break;
      }
      case 'exponential_smoothing_alpha': {
        const interval = finite(
          i.sampleIntervalSeconds,
          'sampleIntervalSeconds'
        );
        const timeConstant = positive(
          i.timeConstantSeconds,
          'timeConstantSeconds'
        );
        result = (
          interval
          / (timeConstant + interval)
        );
        break;
      }
      case 'snr_db':
        result = 20 * Math.log10(
          positive(
            i.signalRms,
            'signalRms'
          ) / positive(
            i.noiseRms,
            'noiseRms'
          )
        );
        break;
      case 'missing_sample_percent':
        result = finite(
          i.missingCount,
          'missingCount'
        ) / positive(
          i.totalCount,
          'totalCount'
        ) * 100;
        break;
      case 'clipping_percent':
        result = finite(
          i.clippedCount,
          'clippedCount'
        ) / positive(
          i.totalCount,
          'totalCount'
        ) * 100;
        break;
      case 'pearson_correlation': {
        const [xValues, yValues] = paired(
          i.xValues,
          i.yValues,
          'xValues',
          'yValues'
        );
        const xMean = mean(xValues);
        const yMean = mean(yValues);
        let numerator = 0;
        let xSquares = 0;
        let ySquares = 0;

        xValues.forEach((xValue, index) => {
          const xDelta = xValue - xMean;
          const yDelta = yValues[index] - yMean;

          numerator += xDelta * yDelta;
          xSquares += xDelta * xDelta;
          ySquares += yDelta * yDelta;
        });

        const denominator = Math.sqrt(
          xSquares * ySquares
        );

        if (denominator === 0) {
          throw new Error(
            'Correlation requires non-constant arrays.'
          );
        }

        result = numerator / denominator;
        break;
      }
      case 'signal_quality_index':
        result = Math.max(
          0,
          Math.min(
            100,
            50
            + 2 * finite(i.snrDb, 'snrDb')
            - 2 * finite(
                i.missingPercent,
                'missingPercent'
              )
            - 3 * finite(
                i.clippingPercent,
                'clippingPercent'
              )
          )
        );
        break;
      default:
        throw new Error(
          `Unsupported biosignal operation: ${operation}`
        );
    }

    return {
      schema:
        'sc-lab-biomedical-biosignal-result/1.0',
      version: VERSION,
      method: definition,
      inputs,
      value: result,
      unit: definition.output.unit,
    };
  }

  function analyzeSignal(
    rawSamples,
    rawSampleRate
  ) {
    const samples = values(
      rawSamples,
      'samples',
      2
    );
    const sampleRateHz = positive(
      rawSampleRate,
      'sampleRateHz'
    );
    const average = mean(samples);
    const rootMeanSquare = rms(samples);
    let crossings = 0;

    for (
      let index = 1;
      index < samples.length;
      index += 1
    ) {
      if (
        (
          samples[index - 1] < 0
          && samples[index] >= 0
        )
        || (
          samples[index - 1] >= 0
          && samples[index] < 0
        )
      ) {
        crossings += 1;
      }
    }

    return {
      schema:
        'sc-lab-biosignal-waveform-analysis/1.0',
      version: VERSION,
      sampleCount: samples.length,
      sampleRateHz,
      durationSeconds:
        (samples.length - 1) / sampleRateHz,
      mean: average,
      standardDeviation:
        standardDeviation(samples),
      rms: rootMeanSquare,
      minimum: Math.min(...samples),
      maximum: Math.max(...samples),
      peakToPeak:
        Math.max(...samples)
        - Math.min(...samples),
      zeroCrossingCount: crossings,
      zeroCrossingRate:
        crossings
        / (samples.length - 1)
        * sampleRateHz,
      crestFactor: rootMeanSquare
        ? Math.max(
            ...samples.map(Math.abs)
          ) / rootMeanSquare
        : 0,
      samples,
    };
  }

  function batchExecute(rows) {
    const results = (rows || []).map(
      (row, index) => {
        try {
          return {
            row: index + 1,
            ok: true,
            result: execute(
              String(row.methodId || ''),
              row.inputs || {}
            ),
          };
        } catch (error) {
          return {
            row: index + 1,
            ok: false,
            error: String(
              error?.message || error
            ),
          };
        }
      }
    );

    return {
      schema:
        'sc-lab-biomedical-biosignal-batch/1.0',
      version: VERSION,
      rowCount: results.length,
      successCount: results.filter(
        (item) => item.ok
      ).length,
      errorCount: results.filter(
        (item) => !item.ok
      ).length,
      results,
    };
  }

  function parseBatchCsv(text) {
    const lines = String(text || '')
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);

    if (lines.length < 2) {
      throw new Error(
        'Batch CSV requires a header and at least one row.'
      );
    }

    function split(line) {
      const values = [];
      let current = '';
      let quoted = false;

      for (
        let index = 0;
        index < line.length;
        index += 1
      ) {
        const character = line[index];

        if (character === '"') {
          if (
            quoted
            && line[index + 1] === '"'
          ) {
            current += '"';
            index += 1;
          } else {
            quoted = !quoted;
          }
        } else if (
          character === ','
          && !quoted
        ) {
          values.push(current.trim());
          current = '';
        } else {
          current += character;
        }
      }

      values.push(current.trim());
      return values;
    }

    const headers = split(lines[0]);

    if (
      headers[0] !== 'methodId'
      || headers[1] !== 'inputsJson'
    ) {
      throw new Error(
        'Batch CSV headers must be methodId,inputsJson.'
      );
    }

    return lines.slice(1).map((line) => {
      const fields = split(line);

      return {
        methodId: fields[0],
        inputs: JSON.parse(fields[1]),
      };
    });
  }

  function formatNumber(value) {
    return Number.isFinite(Number(value))
      ? Number(Number(value).toPrecision(8))
      : value;
  }

  function signalSvg(samples) {
    const width = 900;
    const height = 240;
    const padding = 24;
    const minimum = Math.min(...samples);
    const maximum = Math.max(...samples);
    const range = maximum - minimum || 1;
    const points = samples.map(
      (value, index) => {
        const x = padding
          + index
          / Math.max(1, samples.length - 1)
          * (width - 2 * padding);
        const y = height - padding
          - (value - minimum)
          / range
          * (height - 2 * padding);

        return `${x.toFixed(2)},${y.toFixed(2)}`;
      }
    ).join(' ');

    return `
      <svg
        class="sc-biosignal-svg"
        viewBox="0 0 ${width} ${height}"
        role="img"
        aria-label="Biosignal waveform"
      >
        <line
          x1="${padding}"
          x2="${width - padding}"
          y1="${height / 2}"
          y2="${height / 2}"
          class="sc-biosignal-zero"
        />
        <polyline
          points="${points}"
          class="sc-biosignal-trace"
        />
      </svg>
    `;
  }

  function downloadJson(name, value) {
    if (
      typeof document === 'undefined'
      || typeof Blob === 'undefined'
    ) {
      return false;
    }

    const blob = new Blob(
      [JSON.stringify(value, null, 2)],
      { type: 'application/json' }
    );
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = name;
    link.click();
    URL.revokeObjectURL(url);
    return true;
  }

  function createInputField(input, definition) {
    const isArray = input.type === 'array';
    const benchmark = CATALOG.benchmarks.find(
      (item) => item.methodId === definition.id
    );
    const benchmarkValue = benchmark?.inputs?.[input.key];
    const defaultValue = benchmarkValue !== undefined
      ? (
          isArray
            ? JSON.stringify(benchmarkValue)
            : benchmarkValue
        )
      : (
          isArray
            ? '[1, -1, 1, -1]'
            : (
                input.min !== undefined
                  ? input.min
                  : 1
              )
        );

    return `
      <label>
        ${esc(input.label)}
        <span>${esc(input.unit || '')}</span>
        ${
          isArray
            ? `
              <textarea
                rows="3"
                data-biosignal-input="${esc(input.key)}"
                data-biosignal-type="array"
              >${esc(defaultValue)}</textarea>
            `
            : `
              <input
                type="number"
                step="any"
                value="${esc(defaultValue)}"
                data-biosignal-input="${esc(input.key)}"
                data-biosignal-type="${esc(input.type || 'number')}"
              />
            `
        }
      </label>
    `;
  }

  function render() {
    if (typeof document === 'undefined') {
      return false;
    }

    const roots = Array.from(
      document.querySelectorAll(ROOT_SELECTOR)
    );

    if (!roots.length) {
      return false;
    }

    const root = roots[0];

    roots.slice(1).forEach(
      (duplicate) => duplicate.remove()
    );

    if (
      root.dataset.scBiosignalVersion === VERSION
      && root.querySelector('.sc-biosignal-shell')
    ) {
      state.rendered = true;
      return true;
    }

    root.innerHTML = `
      <section class="sc-biosignal-shell">
        <header class="sc-biosignal-header">
          <p class="sc-biosignal-kicker">
            LAB/BIOMEDICAL/BIOSIGNALS
          </p>
          <h3>Biomedical Engineering and Biosignals</h3>
          <p>
            Auditable calculations and non-clinical signal
            analysis for ECG, PPG, respiration, EMG, EEG,
            acquisition design, filtering, and signal quality.
          </p>
          <div class="sc-biosignal-status">
            <span>48 validated methods</span>
            <span>48 deterministic benchmarks</span>
            <span>8 engineering categories</span>
          </div>
        </header>

        <div class="sc-biosignal-tabs" role="tablist">
          <button type="button" data-biosignal-tab="calculator">
            Method calculator
          </button>
          <button type="button" data-biosignal-tab="waveform">
            Waveform analysis
          </button>
          <button type="button" data-biosignal-tab="batch">
            Batch execution
          </button>
        </div>

        <section data-biosignal-panel="calculator">
          <div class="sc-biosignal-grid">
            <section class="sc-biosignal-card">
              <label>
                Category
                <select data-biosignal-category>
                  ${CATALOG.categories.map(
                    (category) => `
                      <option value="${esc(category.id)}">
                        ${esc(category.label)}
                      </option>
                    `
                  ).join('')}
                </select>
              </label>
              <label>
                Method
                <select data-biosignal-method></select>
              </label>
              <div
                class="sc-biosignal-inputs"
                data-biosignal-inputs
              ></div>
              <div class="sc-biosignal-actions">
                <button type="button" data-biosignal-run>
                  Run calculation
                </button>
                <button type="button" data-biosignal-export>
                  Export JSON
                </button>
                <button type="button" data-biosignal-provenance>
                  Create provenance record
                </button>
              </div>
            </section>

            <section class="sc-biosignal-card">
              <h4>Calculation output</h4>
              <pre data-biosignal-output aria-live="polite">
Select a method and run the calculation.
              </pre>
            </section>
          </div>
        </section>

        <section data-biosignal-panel="waveform" hidden>
          <div class="sc-biosignal-grid">
            <section class="sc-biosignal-card">
              <label>
                Sample rate
                <span>Hz</span>
                <input
                  type="number"
                  step="any"
                  value="100"
                  data-biosignal-wave-rate
                />
              </label>
              <label>
                Signal samples
                <textarea
                  rows="10"
                  data-biosignal-wave-samples
                >0,0.4,0.8,0.2,-0.5,-1,-0.3,0.5,0.9,0.1,-0.6,-0.9</textarea>
              </label>
              <div class="sc-biosignal-actions">
                <button type="button" data-biosignal-wave-run>
                  Analyze waveform
                </button>
                <button type="button" data-biosignal-project>
                  Send to project
                </button>
                <button type="button" data-biosignal-notebook>
                  Send to notebook
                </button>
              </div>
            </section>

            <section class="sc-biosignal-card">
              <h4>Waveform and features</h4>
              <div data-biosignal-chart></div>
              <pre data-biosignal-wave-output aria-live="polite">
Run waveform analysis to calculate signal features.
              </pre>
            </section>
          </div>
        </section>

        <section data-biosignal-panel="batch" hidden>
          <div class="sc-biosignal-grid">
            <section class="sc-biosignal-card">
              <label>
                Batch CSV
                <span>methodId,inputsJson</span>
                <textarea
                  rows="12"
                  data-biosignal-batch-csv
                >methodId,inputsJson
heart-rate-from-rr,"{""rrSeconds"":0.8}"
emg-rms,"{""samples"":[1,-1,1,-1]}"
signal-quality-index,"{""snrDb"":20,""missingPercent"":2,""clippingPercent"":1}"</textarea>
              </label>
              <div class="sc-biosignal-actions">
                <button type="button" data-biosignal-batch-run>
                  Run batch
                </button>
                <button type="button" data-biosignal-batch-export>
                  Export batch JSON
                </button>
              </div>
            </section>

            <section class="sc-biosignal-card">
              <h4>Batch output</h4>
              <pre data-biosignal-batch-output aria-live="polite">
Run the batch to inspect row-level results.
              </pre>
            </section>
          </div>
        </section>

        <p class="sc-biosignal-boundary">
          Research, education, and prototyping only. This
          workspace is not for diagnosis, treatment, clinical
          monitoring, alarms, or patient-specific decisions.
          Validate sensors, algorithms, and interpretations
          independently before any regulated or clinical use.
        </p>
      </section>
    `;

    const categorySelect = root.querySelector(
      '[data-biosignal-category]'
    );
    const methodSelect = root.querySelector(
      '[data-biosignal-method]'
    );
    const inputsContainer = root.querySelector(
      '[data-biosignal-inputs]'
    );
    const output = root.querySelector(
      '[data-biosignal-output]'
    );

    function show(element, value) {
      element.textContent = JSON.stringify(
        value,
        null,
        2
      );
    }

    function methodsForCategory() {
      return CATALOG.methods.filter(
        (item) => (
          item.category === categorySelect.value
        )
      );
    }

    function loadMethods() {
      const options = methodsForCategory();

      methodSelect.innerHTML = options.map(
        (item) => `
          <option value="${esc(item.id)}">
            ${esc(item.label)}
          </option>
        `
      ).join('');

      loadInputs();
    }

    function loadInputs() {
      const definition = method(
        methodSelect.value
      );

      inputsContainer.innerHTML = definition
        ? definition.inputs
            .map(
              (input) => createInputField(
                input,
                definition
              )
            )
            .join('')
        : '';
    }

    function readInputs() {
      const definition = method(
        methodSelect.value
      );
      const result = {};

      definition.inputs.forEach((input) => {
        const field = root.querySelector(
          `[data-biosignal-input="${CSS.escape(input.key)}"]`
        );

        result[input.key] = (
          input.type === 'array'
            ? values(
                field.value,
                input.label,
                input.minItems || 1
              )
            : Number(field.value)
        );
      });

      return result;
    }

    categorySelect.addEventListener(
      'change',
      loadMethods
    );
    methodSelect.addEventListener(
      'change',
      loadInputs
    );

    root.querySelector(
      '[data-biosignal-run]'
    ).addEventListener(
      'click',
      () => {
        try {
          state.currentResult = execute(
            methodSelect.value,
            readInputs()
          );
          state.lastError = null;
          show(output, state.currentResult);
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show(output, {
            error: state.lastError,
          });
        }
      }
    );

    root.querySelector(
      '[data-biosignal-export]'
    ).addEventListener(
      'click',
      () => downloadJson(
        `sc-lab-biosignal-result-${Date.now()}.json`,
        state.currentResult || {
          version: VERSION,
          methods: CATALOG.methods,
        }
      )
    );

    root.querySelector(
      '[data-biosignal-provenance]'
    ).addEventListener(
      'click',
      () => {
        try {
          if (!state.currentResult) {
            throw new Error(
              'Run a calculation before creating a provenance record.'
            );
          }

          const provenance =
            Lab.BioprocessValidationProvenance;

          if (
            !provenance
            || typeof provenance.createRecord
              !== 'function'
          ) {
            throw new Error(
              'The v0.22.3 provenance engine is unavailable.'
            );
          }

          state.provenanceRecord =
            provenance.createRecord(
              state.currentResult,
              {
                eventType:
                  'validation-decision',
                profileId:
                  'biomedical-biosignal-calculation',
                notes:
                  'Non-clinical biosignal calculation handoff.',
                disposition:
                  'research-review',
              }
            );
          show(output, state.provenanceRecord);
        } catch (error) {
          state.lastError = String(
            error?.message || error
          );
          show(output, {
            error: state.lastError,
          });
        }
      }
    );

    root.querySelectorAll(
      '[data-biosignal-tab]'
    ).forEach((button) => {
      button.addEventListener(
        'click',
        () => {
          root.querySelectorAll(
            '[data-biosignal-panel]'
          ).forEach((panel) => {
            panel.hidden = (
              panel.dataset.biosignalPanel
              !== button.dataset.biosignalTab
            );
          });
        }
      );
    });

    const waveSamples = root.querySelector(
      '[data-biosignal-wave-samples]'
    );
    const waveRate = root.querySelector(
      '[data-biosignal-wave-rate]'
    );
    const waveOutput = root.querySelector(
      '[data-biosignal-wave-output]'
    );
    const chart = root.querySelector(
      '[data-biosignal-chart]'
    );

    root.querySelector(
      '[data-biosignal-wave-run]'
    ).addEventListener(
      'click',
      () => {
        try {
          state.waveformResult = analyzeSignal(
            waveSamples.value,
            waveRate.value
          );
          chart.innerHTML = signalSvg(
            state.waveformResult.samples
          );
          show(
            waveOutput,
            {
              ...state.waveformResult,
              samples: undefined,
            }
          );
        } catch (error) {
          show(waveOutput, {
            error: String(
              error?.message || error
            ),
          });
        }
      }
    );

    function dispatchHandoff(eventName) {
      if (!state.waveformResult) {
        throw new Error(
          'Run waveform analysis first.'
        );
      }

      document.dispatchEvent(
        new CustomEvent(
          eventName,
          {
            detail: {
              source: 'biomedical-biosignals',
              version: VERSION,
              record: state.waveformResult,
            },
          }
        )
      );
    }

    root.querySelector(
      '[data-biosignal-project]'
    ).addEventListener(
      'click',
      () => {
        try {
          dispatchHandoff(
            'sc-lab:project-record'
          );
          show(waveOutput, {
            status: 'project-handoff-dispatched',
            record: state.waveformResult,
          });
        } catch (error) {
          show(waveOutput, {
            error: String(
              error?.message || error
            ),
          });
        }
      }
    );

    root.querySelector(
      '[data-biosignal-notebook]'
    ).addEventListener(
      'click',
      () => {
        try {
          dispatchHandoff(
            'sc-lab:notebook-entry'
          );
          show(waveOutput, {
            status: 'notebook-handoff-dispatched',
            record: state.waveformResult,
          });
        } catch (error) {
          show(waveOutput, {
            error: String(
              error?.message || error
            ),
          });
        }
      }
    );

    const batchCsv = root.querySelector(
      '[data-biosignal-batch-csv]'
    );
    const batchOutput = root.querySelector(
      '[data-biosignal-batch-output]'
    );

    root.querySelector(
      '[data-biosignal-batch-run]'
    ).addEventListener(
      'click',
      () => {
        try {
          state.batchResult = batchExecute(
            parseBatchCsv(batchCsv.value)
          );
          show(batchOutput, state.batchResult);
        } catch (error) {
          show(batchOutput, {
            error: String(
              error?.message || error
            ),
          });
        }
      }
    );

    root.querySelector(
      '[data-biosignal-batch-export]'
    ).addEventListener(
      'click',
      () => downloadJson(
        `sc-lab-biosignal-batch-${Date.now()}.json`,
        state.batchResult || {
          version: VERSION,
          rowCount: 0,
          results: [],
        }
      )
    );

    loadMethods();
    root.dataset.scBiosignalVersion = VERSION;
    state.rendered = true;
    state.lastError = null;
    return true;
  }

  function init() {
    [0, 80, 220, 600, 1400].forEach(
      (delay) => {
        W.setTimeout(render, delay);
      }
    );

    if (
      typeof MutationObserver !== 'undefined'
      && typeof document !== 'undefined'
    ) {
      const observer = new MutationObserver(
        () => render()
      );

      observer.observe(
        document.documentElement,
        {
          childList: true,
          subtree: true,
        }
      );
    }
  }

  function status() {
    const root = typeof document === 'undefined'
      ? null
      : document.querySelector(ROOT_SELECTOR);

    return {
      version: VERSION,
      methodCount: CATALOG.methods.length,
      benchmarkCount:
        CATALOG.benchmarks.length,
      categoryCount:
        CATALOG.categories.length,
      rootFound: Boolean(root),
      rendered: Boolean(
        root?.querySelector(
          '.sc-biosignal-shell'
        )
      ),
      lastError: state.lastError,
    };
  }

  Lab.BiomedicalEngineeringBiosignals = {
    VERSION,
    definitions: CATALOG.methods,
    benchmarks: CATALOG.benchmarks,
    categories: CATALOG.categories,
    execute,
    analyzeSignal,
    batchExecute,
    parseBatchCsv,
    render,
    init,
    status,
    state,
  };

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener(
        'DOMContentLoaded',
        init,
        { once: true }
      );
    } else {
      init();
    }
  }
})();
