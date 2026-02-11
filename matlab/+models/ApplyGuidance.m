function interceptor = ApplyGuidance(interceptor, commandedHeading, dt)
%APPLYGUIDANCE Apply turn-rate-limited heading command.
    headingError = utils.WrapAngle(commandedHeading - interceptor.heading);
    maxDelta = interceptor.maxTurnRate * dt;
    clamped = min(max(headingError, -maxDelta), maxDelta);
    interceptor.heading = utils.WrapAngle(interceptor.heading + clamped);
end
