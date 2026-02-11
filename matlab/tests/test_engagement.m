function tests = test_engagement
%TEST_ENGAGEMENT Unit tests for engagement phase progression.
    tests = functiontests(localfunctions);
end

function setupOnce(~)
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
    addpath(genpath(projectRoot));
end

function testPhaseProgressionToComplete(testCase)
    scenario = sim.DefaultScenario();
    scenario.target.position = [800, 200];
    scenario.target.speed = 20;
    scenario.target.waypoints = [0, 0];

    scenario.surveillanceSensor.position = [0, 0];
    scenario.surveillanceSensor.max_range = 5000;
    scenario.surveillanceSensor.pd_at_max_range = 1.0;
    scenario.surveillanceSensor.classification_accuracy = 1.0;
    scenario.surveillanceSensor.noise.range_noise_fraction = 0.0;
    scenario.surveillanceSensor.noise.bearing_noise_deg = 0.0;
    scenario.surveillanceSensor.noise.speed_noise_fraction = 0.0;
    scenario.surveillanceSensor.noise.heading_noise_deg = 0.0;

    scenario.interceptor.position = [0, -100];
    scenario.interceptor.max_speed = 120;
    scenario.interceptor.max_turn_rate_deg = 90;
    scenario.interceptor.kill_radius = 12;
    scenario.interceptor.max_flight_time = 120;

    scenario.engagement.terminal_handover_range = 250;
    scenario.engagement.stern_offset = 0;

    scenario.simulation.dt = 0.1;
    scenario.simulation.max_time = 120;
    scenario.simulation.seed = 7;

    [history, ~] = sim.SimulationRunner(scenario);

    phaseValues = string(history.Phase);
    resultFinal = string(history.Result(end));

    verifyTrue(testCase, any(phaseValues == "SEARCH"));
    verifyTrue(testCase, any(phaseValues == "TRACK"));
    verifyTrue(testCase, any(phaseValues == "CLASSIFY"));
    verifyTrue(testCase, any(phaseValues == "LAUNCH"));
    verifyTrue(testCase, any(phaseValues == "MIDCOURSE"));
    verifyTrue(testCase, any(phaseValues == "TERMINAL"));
    verifyTrue(testCase, any(phaseValues == "COMPLETE"));
    verifyTrue(testCase, resultFinal == "HIT" || resultFinal == "MISS");
end

function testMissWhenInterceptorTimesOut(testCase)
    scenario = sim.DefaultScenario();
    scenario.target.position = [5000, 0];
    scenario.target.speed = 40;
    scenario.target.waypoints = [0, 0];

    scenario.surveillanceSensor.max_range = 10000;
    scenario.surveillanceSensor.pd_at_max_range = 1.0;
    scenario.surveillanceSensor.classification_accuracy = 1.0;

    scenario.interceptor.position = [0, 0];
    scenario.interceptor.max_speed = 20;
    scenario.interceptor.max_flight_time = 5;
    scenario.interceptor.kill_radius = 2;

    scenario.engagement.terminal_handover_range = 50;
    scenario.simulation.max_time = 30;
    scenario.simulation.seed = 1;

    [history, ~] = sim.SimulationRunner(scenario);
    verifyEqual(testCase, string(history.Result(end)), "MISS");
end
