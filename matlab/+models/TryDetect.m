function detected = TryDetect(sensor, sensorPos, targetPos)
%TRYDETECT Stochastic target detection.
    if ~models.InFieldOfRegard(sensor, sensorPos, targetPos)
        detected = false;
        return;
    end

    targetRange = utils.Distance(sensorPos, targetPos);
    pd = models.DetectionProbability(sensor, targetRange);
    detected = rand() < pd;
end
