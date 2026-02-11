function cmdHeading = ProNav(interceptorPos, interceptorVel, targetPos, targetVel, navGain)
%PRONAV Proportional navigation terminal guidance.
    if nargin < 5 || isempty(navGain)
        navGain = 4.0;
    end

    losAngle = utils.Bearing(interceptorPos, targetPos);
    losRate = utils.LineOfSightRate(interceptorPos, interceptorVel, targetPos, targetVel);
    vc = utils.ClosingSpeed(interceptorPos, interceptorVel, targetPos, targetVel);
    if abs(vc) < 1e-3
        cmdHeading = losAngle;
        return;
    end

    headingCorrection = navGain * losRate;
    cmdHeading = losAngle + headingCorrection;
end


