function pd = DetectionProbability(sensor, targetRange)
%DETECTIONPROBABILITY Probability of detection as function of range.
    if targetRange > sensor.maxRange
        pd = 0.0;
        return;
    end
    fraction = targetRange / max(sensor.maxRange, 1e-6);
    pd = 1.0 - fraction * (1.0 - sensor.pdAtMaxRange);
end
