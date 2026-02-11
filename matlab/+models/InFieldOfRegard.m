function inFor = InFieldOfRegard(sensor, sensorPos, targetPos)
%INFIELDOFREGARD True if target is inside sensor field of regard.
    if sensor.fieldOfRegard >= 2*pi
        inFor = true;
        return;
    end

    angleToTarget = utils.Bearing(sensorPos, targetPos);
    angularOffset = abs(utils.WrapAngle(angleToTarget - sensor.boresight));
    inFor = angularOffset <= sensor.fieldOfRegard / 2.0;
end
