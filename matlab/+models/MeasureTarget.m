function measurement = MeasureTarget(sensor, sensorPos, targetPos, targetSpeed, targetHeading)
%MEASURETARGET Produce noisy target state estimate from surveillance sensor.
    trueRange = utils.Distance(sensorPos, targetPos);
    trueBearing = utils.Bearing(sensorPos, targetPos);

    rangeSigma = sensor.rangeNoiseFraction * trueRange;
    bearingSigma = sensor.bearingNoiseRad;
    speedSigma = sensor.speedNoiseFraction * targetSpeed;
    headingSigma = sensor.headingNoiseRad;

    if rangeSigma > 0
        measRange = max(0.0, trueRange + randn() * rangeSigma);
    else
        measRange = trueRange;
    end

    if bearingSigma > 0
        measBearing = trueBearing + randn() * bearingSigma;
    else
        measBearing = trueBearing;
    end

    if speedSigma > 0
        measSpeed = max(0.0, targetSpeed + randn() * speedSigma);
    else
        measSpeed = targetSpeed;
    end

    if headingSigma > 0
        measHeading = targetHeading + randn() * headingSigma;
    else
        measHeading = targetHeading;
    end

    estPos = sensorPos + measRange * utils.UnitVector(measBearing);
    estVel = measSpeed * utils.UnitVector(measHeading);

    measurement = struct();
    measurement.measuredRange = measRange;
    measurement.measuredBearing = measBearing;
    measurement.measuredSpeed = measSpeed;
    measurement.measuredHeading = measHeading;
    measurement.estimatedPosition = estPos;
    measurement.estimatedVelocity = estVel;
    measurement.trueRange = trueRange;
    measurement.trueBearing = trueBearing;
    measurement.trueSpeed = targetSpeed;
    measurement.trueHeading = targetHeading;
end
