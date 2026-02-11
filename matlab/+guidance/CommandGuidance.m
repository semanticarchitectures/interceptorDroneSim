function cmdHeading = CommandGuidance(sensorPos, targetPos, interceptorPos, estimatedTargetVel, sternOffset, approachBlendRange)
%COMMANDGUIDANCE Midcourse command guidance with optional stern attack.
    if nargin < 4
        estimatedTargetVel = [];
    end
    if nargin < 5 || isempty(sternOffset)
        sternOffset = 0.0;
    end
    if nargin < 6 || isempty(approachBlendRange)
        approachBlendRange = 500.0;
    end

    if isempty(estimatedTargetVel) || sternOffset <= 0.0
        cmdHeading = utils.Bearing(interceptorPos, targetPos);
        return;
    end

    velNorm = norm(estimatedTargetVel);
    if velNorm < 1e-6
        cmdHeading = utils.Bearing(interceptorPos, targetPos);
        return;
    end

    velUnit = estimatedTargetVel / velNorm;
    sternPoint = targetPos - sternOffset * velUnit;
    trueRange = utils.Distance(interceptorPos, targetPos);

    if trueRange >= approachBlendRange
        aimPoint = sternPoint;
    else
        blend = trueRange / max(approachBlendRange, 1e-6);
        aimPoint = (1.0 - blend) * targetPos + blend * sternPoint;
    end

    cmdHeading = utils.Bearing(interceptorPos, aimPoint);
end


