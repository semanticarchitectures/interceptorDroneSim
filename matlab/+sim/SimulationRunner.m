function [history, context] = SimulationRunner(scenarioInput, varargin)
%SIMULATIONRUNNER Run fixed-step interceptor engagement simulation.
%
%   [history, context] = sim.SimulationRunner() uses default scenario.
%   [history, context] = sim.SimulationRunner("path/to/scenario.json") loads a file.
%   [history, context] = sim.SimulationRunner(scenarioStruct) uses provided config.
%
%   Name-value:
%       "Seed"  - Override RNG seed.

    if nargin < 1
        scenarioInput = [];
    end

    p = inputParser;
    p.addParameter("Seed", [], @(x) isempty(x) || (isscalar(x) && isnumeric(x)));
    p.parse(varargin{:});
    seedOverride = p.Results.Seed;

    scenario = sim.ScenarioLoader(scenarioInput);
    seed = scenario.simulation.seed;
    if ~isempty(seedOverride)
        seed = seedOverride;
    end
    if ~isempty(seed)
        rng(seed, "twister");
    end

    dt = scenario.simulation.dt;
    maxTime = scenario.simulation.max_time;

    target = models.InitTarget(scenario.target);
    interceptor = models.InitInterceptor(scenario.interceptor);
    surveillanceSensor = models.InitSensor(scenario.surveillanceSensor);
    sensorPosition = reshape(scenario.surveillanceSensor.position, 1, 2);
    launchPosition = interceptor.pos;

    engagementState = engagement.InitEngagement(target, interceptor, surveillanceSensor, sensorPosition, scenario.engagement);

    maxSteps = floor(maxTime / dt) + 2;
    times = nan(maxSteps, 1);
    targetPos = nan(maxSteps, 2);
    interceptorPos = nan(maxSteps, 2);
    phaseIdx = nan(maxSteps, 1);
    resultIdx = nan(maxSteps, 1);
    estTargetPos = nan(maxSteps, 2);
    estTargetVel = nan(maxSteps, 2);
    interceptorSpeed = nan(maxSteps, 1);
    targetActive = false(maxSteps, 1);

    simTime = 0.0;
    k = 1;
    [times, targetPos, interceptorPos, phaseIdx, resultIdx, estTargetPos, estTargetVel, interceptorSpeed, targetActive] = ...
        localRecord(k, simTime, target, interceptor, engagementState, times, targetPos, interceptorPos, phaseIdx, resultIdx, estTargetPos, estTargetVel, interceptorSpeed, targetActive);

    while simTime < maxTime && engagementState.phase ~= uint8(7)
        target = models.StepTarget(target, dt);
        interceptor = models.StepInterceptor(interceptor, dt);
        [engagementState, target, interceptor] = engagement.StepEngagement(engagementState, target, interceptor, surveillanceSensor, sensorPosition, simTime, dt);

        simTime = simTime + dt;
        k = k + 1;
        [times, targetPos, interceptorPos, phaseIdx, resultIdx, estTargetPos, estTargetVel, interceptorSpeed, targetActive] = ...
            localRecord(k, simTime, target, interceptor, engagementState, times, targetPos, interceptorPos, phaseIdx, resultIdx, estTargetPos, estTargetVel, interceptorSpeed, targetActive);
    end

    times = times(1:k);
    targetPos = targetPos(1:k, :);
    interceptorPos = interceptorPos(1:k, :);
    phaseIdx = phaseIdx(1:k);
    resultIdx = resultIdx(1:k);
    estTargetPos = estTargetPos(1:k, :);
    estTargetVel = estTargetVel(1:k, :);
    interceptorSpeed = interceptorSpeed(1:k);
    targetActive = targetActive(1:k);

    phase = categorical(engagementState.phaseNames(phaseIdx), engagementState.phaseNames, engagementState.phaseNames);
    result = categorical(engagementState.resultNames(resultIdx), engagementState.resultNames, engagementState.resultNames);

    history = timetable(seconds(times), targetPos, interceptorPos, estTargetPos, estTargetVel, phase, result, interceptorSpeed, targetActive, ...
        'VariableNames', {"TargetPos", "InterceptorPos", "EstTargetPos", "EstTargetVel", "Phase", "Result", "InterceptorSpeed", "TargetActive"});
    history.TimeSeconds = times;

    context = struct();
    context.scenario = scenario;
    context.target = target;
    context.interceptor = interceptor;
    context.surveillanceSensor = surveillanceSensor;
    context.engagement = engagementState;
    context.sensorPosition = sensorPosition;
    context.launchPosition = launchPosition;
    context.protectedAssetPosition = sensorPosition;
end

function [times, targetPos, interceptorPos, phaseIdx, resultIdx, estTargetPos, estTargetVel, interceptorSpeed, targetActive] = localRecord(k, simTime, target, interceptor, engagementState, times, targetPos, interceptorPos, phaseIdx, resultIdx, estTargetPos, estTargetVel, interceptorSpeed, targetActive)

    times(k) = simTime;
    targetPos(k, :) = target.pos;
    interceptorPos(k, :) = interceptor.pos;
    phaseIdx(k) = double(engagementState.phase);
    resultIdx(k) = double(engagementState.result);
    estTargetPos(k, :) = engagementState.estimatedTargetPos;
    estTargetVel(k, :) = engagementState.estimatedTargetVel;
    interceptorSpeed(k) = interceptor.speed;
    targetActive(k) = target.active;
end
