function tests = test_utils_guidance
%TEST_UTILS_GUIDANCE Unit tests for utility and guidance functions.
    tests = functiontests(localfunctions);
end

function setupOnce(testCase)
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
    addpath(genpath(projectRoot));
    testCase.TestData.projectRoot = projectRoot;
end

function testDistanceAndBearing(testCase)
    p0 = [0, 0];
    p1 = [3, 4];
    verifyEqual(testCase, utils.Distance(p0, p1), 5.0, "AbsTol", 1e-12);
    verifyEqual(testCase, utils.Bearing([0, 0], [1, 1]), pi/4, "AbsTol", 1e-12);
end

function testWrapAngleRange(testCase)
    a = utils.WrapAngle(3*pi);
    verifyTrue(testCase, a >= -pi && a <= pi);
    verifyEqual(testCase, a, -pi, "AbsTol", 1e-12);
end

function testPurePursuit(testCase)
    cmd = guidance.PurePursuit([0, 0], [0, 10]);
    verifyEqual(testCase, cmd, pi/2, "AbsTol", 1e-12);
end

function testCommandGuidanceDirectWhenNoVelocity(testCase)
    sensorPos = [0, 0];
    targetPos = [100, 20];
    interceptorPos = [10, -5];
    direct = utils.Bearing(interceptorPos, targetPos);
    cmd = guidance.CommandGuidance(sensorPos, targetPos, interceptorPos, [], 0, 500);
    verifyEqual(testCase, cmd, direct, "AbsTol", 1e-12);
end

function testCommandGuidanceSternAttack(testCase)
    sensorPos = [0, 0];
    targetPos = [100, 100];
    interceptorPos = [0, 0];
    estVel = [1, 0];

    direct = utils.Bearing(interceptorPos, targetPos);
    cmd = guidance.CommandGuidance(sensorPos, targetPos, interceptorPos, estVel, 20, 50);
    verifyGreaterThan(testCase, abs(cmd - direct), 1e-6);
end

function testProNavFinite(testCase)
    cmd = guidance.ProNav([0, 0], [100, 0], [1000, 100], [20, 0], 4.0);
    verifyTrue(testCase, isfinite(cmd));
end
