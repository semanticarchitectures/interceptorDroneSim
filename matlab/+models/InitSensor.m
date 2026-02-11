function sensor = InitSensor(cfg)
%INITSENSOR Build sensor configuration struct.
    sensor = struct();
    sensor.maxRange = localGet(cfg, "max_range", 5000.0);
    sensor.fieldOfRegard = deg2rad(localGet(cfg, "field_of_regard_deg", 360.0));
    sensor.boresight = deg2rad(localGet(cfg, "boresight_deg", 0.0));
    sensor.pdAtMaxRange = localGet(cfg, "pd_at_max_range", 0.3);
    sensor.classificationAccuracy = localGet(cfg, "classification_accuracy", 0.8);

    noiseCfg = localGet(cfg, "noise", struct());
    sensor.rangeNoiseFraction = localGet(noiseCfg, "range_noise_fraction", 0.0);
    sensor.bearingNoiseRad = deg2rad(localGet(noiseCfg, "bearing_noise_deg", 0.0));
    sensor.speedNoiseFraction = localGet(noiseCfg, "speed_noise_fraction", 0.0);
    sensor.headingNoiseRad = deg2rad(localGet(noiseCfg, "heading_noise_deg", 0.0));
end

function value = localGet(s, fieldName, defaultValue)
    if isfield(s, fieldName)
        value = s.(fieldName);
    else
        value = defaultValue;
    end
end
