function engagement = InitEngagement(target, interceptor, surveillanceSensor, sensorPosition, cfg)
%INITENGAGEMENT Build engagement state struct.
    if nargin < 5
        cfg = struct();
    end

    engagement = struct();
    engagement.phaseNames = ["SEARCH","TRACK","CLASSIFY","LAUNCH","MIDCOURSE","TERMINAL","COMPLETE"];
    engagement.resultNames = ["PENDING","HIT","MISS","TIMEOUT"];

    engagement.phase = uint8(1);
    engagement.result = uint8(1);

    engagement.terminalGuidance = lower(string(localGet(cfg, "terminal_guidance", "proportional_nav")));
    engagement.navGain = localGet(cfg, "nav_gain", 4.0);
    engagement.terminalHandoverRange = localGet(cfg, "terminal_handover_range", 100.0);
    engagement.sternOffset = localGet(cfg, "stern_offset", 0.0);
    engagement.approachBlendRange = localGet(cfg, "approach_blend_range", 500.0);

    engagement.trackDetected = false;
    engagement.trackDetectionCount = 0;
    engagement.trackConfirmThreshold = 3;
    engagement.trackConfirmed = false;

    engagement.classConfidence = 0.0;
    engagement.classThreshold = localGet(cfg, "classification_threshold", 0.8);
    engagement.classLooks = 0;
    engagement.classified = false;

    engagement.phaseLogTimes = zeros(0, 1);
    engagement.phaseLogPhases = strings(0, 1);

    engagement.estimatedTargetPos = [NaN, NaN];
    engagement.estimatedTargetVel = [NaN, NaN];
    engagement.latestMeasurement = struct();

    engagement.sensorPosition = reshape(sensorPosition, 1, 2);
    engagement.targetName = string(target.name);
    engagement.interceptorName = string(interceptor.name);
    engagement.sensorMaxRange = surveillanceSensor.maxRange;
end

function value = localGet(s, fieldName, defaultValue)
    if isfield(s, fieldName)
        value = s.(fieldName);
    else
        value = defaultValue;
    end
end
