function [engagement, target, interceptor] = StepEngagement(engagement, target, interceptor, surveillanceSensor, sensorPosition, simTime, dt)
%STEPENGAGEMENT Advance kill-chain state machine one step.
    COMPLETE = uint8(7);
    MIDCOURSE = uint8(5);
    TERMINAL = uint8(6);

    if engagement.phase == COMPLETE
        return;
    end

    switch engagement.phase
        case uint8(1) % SEARCH
            detected = models.TryDetect(surveillanceSensor, sensorPosition, target.pos);
            [engagement.trackDetected, engagement.trackDetectionCount, engagement.trackConfirmed] = localProcessDetection(engagement.trackDetected, engagement.trackDetectionCount, engagement.trackConfirmThreshold, engagement.trackConfirmed, detected);
            if engagement.trackDetected
                engagement = localTransition(engagement, uint8(2), simTime);
            end

        case uint8(2) % TRACK
            detected = models.TryDetect(surveillanceSensor, sensorPosition, target.pos);
            [engagement.trackDetected, engagement.trackDetectionCount, engagement.trackConfirmed] = localProcessDetection(engagement.trackDetected, engagement.trackDetectionCount, engagement.trackConfirmThreshold, engagement.trackConfirmed, detected);
            if engagement.trackConfirmed
                engagement = localTransition(engagement, uint8(3), simTime);
            end

        case uint8(3) % CLASSIFY
            if ~engagement.classified
                engagement.classLooks = engagement.classLooks + 1;
                correct = models.TryClassify(surveillanceSensor);
                if correct
                    engagement.classConfidence = engagement.classConfidence + (1.0 - engagement.classConfidence) * 0.3;
                else
                    engagement.classConfidence = engagement.classConfidence * 0.7;
                end
                if engagement.classConfidence >= engagement.classThreshold
                    engagement.classified = true;
                end
            end
            if engagement.classified
                engagement = localTransition(engagement, uint8(4), simTime);
            end

        case uint8(4) % LAUNCH
            launchHeading = utils.Bearing(interceptor.pos, target.pos);
            interceptor = models.LaunchInterceptor(interceptor, launchHeading);
            engagement = localTransition(engagement, MIDCOURSE, simTime);

        case MIDCOURSE
            if interceptor.state == "MISSED"
                engagement.result = uint8(3);
                engagement = localTransition(engagement, COMPLETE, simTime);
                return;
            end

            measurement = models.MeasureTarget(surveillanceSensor, sensorPosition, target.pos, target.speed, target.heading);
            engagement.latestMeasurement = measurement;
            engagement.estimatedTargetPos = measurement.estimatedPosition;
            engagement.estimatedTargetVel = measurement.estimatedVelocity;

            cmdHeading = guidance.CommandGuidance(sensorPosition, engagement.estimatedTargetPos, interceptor.pos, engagement.estimatedTargetVel, engagement.sternOffset, engagement.approachBlendRange);
            interceptor = models.ApplyGuidance(interceptor, cmdHeading, dt);

            estRange = utils.Distance(interceptor.pos, engagement.estimatedTargetPos);
            if estRange <= engagement.terminalHandoverRange
                interceptor.state = "TERMINAL";
                engagement = localTransition(engagement, TERMINAL, simTime);
            end

        case TERMINAL
            if models.CheckIntercept(interceptor, target.pos)
                interceptor.state = "DETONATED";
                target.active = false;
                engagement.result = uint8(2);
                engagement = localTransition(engagement, COMPLETE, simTime);
                return;
            end

            if interceptor.state == "MISSED"
                engagement.result = uint8(3);
                engagement = localTransition(engagement, COMPLETE, simTime);
                return;
            end

            if engagement.terminalGuidance == "proportional_nav"
                interceptorVel = interceptor.speed * utils.UnitVector(interceptor.heading);
                targetVel = target.speed * utils.UnitVector(target.heading);
                cmdHeading = guidance.ProNav(interceptor.pos, interceptorVel, target.pos, targetVel, engagement.navGain);
            else
                cmdHeading = guidance.PurePursuit(interceptor.pos, target.pos);
            end
            interceptor = models.ApplyGuidance(interceptor, cmdHeading, dt);
    end
end

function [detectedState, detectionCount, trackConfirmed] = localProcessDetection(detectedState, detectionCount, confirmThreshold, trackConfirmed, detected)
    if detected
        detectionCount = detectionCount + 1;
        detectedState = true;
        if detectionCount >= confirmThreshold
            trackConfirmed = true;
        end
    end
end

function engagement = localTransition(engagement, nextPhase, simTime)
    engagement.phase = nextPhase;
    engagement.phaseLogTimes(end+1, 1) = simTime;
    engagement.phaseLogPhases(end+1, 1) = engagement.phaseNames(nextPhase);
end
