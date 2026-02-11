function tests = test_scenario_loader
%TEST_SCENARIO_LOADER Unit tests for loader and validation.
    tests = functiontests(localfunctions);
end

function setupOnce(~)
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
    addpath(genpath(projectRoot));
end

function testDefaultScenarioValid(testCase)
    scenario = sim.DefaultScenario();
    validated = sim.ValidateScenario(scenario);
    verifyTrue(testCase, isstruct(validated));
    verifyGreaterThan(testCase, validated.simulation.dt, 0);
end

function testInvalidDtThrows(testCase)
    scenario = sim.DefaultScenario();
    scenario.simulation.dt = 0;
    verifyError(testCase, @() sim.ValidateScenario(scenario), 'sim:ValidateScenario:InvalidValue');
end

function testSnakeCaseSensorAlias(testCase)
    defaultScenario = sim.DefaultScenario();

    raw = struct();
    raw.target = defaultScenario.target;
    raw.interceptor = defaultScenario.interceptor;
    raw.engagement = defaultScenario.engagement;
    raw.simulation = defaultScenario.simulation;
    raw.surveillance_sensor = defaultScenario.surveillanceSensor;

    scenario = sim.ScenarioLoader(raw);
    verifyTrue(testCase, isfield(scenario, 'surveillanceSensor'));
    verifyTrue(testCase, isfield(scenario.surveillanceSensor, 'max_range'));
end
