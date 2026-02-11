%RUN_EXAMPLE Run default or file-driven MATLAB digital twin scenario.
clear;
clc;

addpath(genpath(fileparts(mfilename('fullpath'))));

scenarioPath = fullfile(fileparts(mfilename('fullpath')), 'scenarios', 'example_intercept.json');
if isfile(scenarioPath)
    [history, context] = sim.SimulationRunner(scenarioPath, 'Seed', 42);
else
    [history, context] = sim.SimulationRunner(sim.DefaultScenario(), 'Seed', 42);
end

analysis.PlotTrajectories(history, ...
    'SensorPosition', context.sensorPosition, ...
    'LaunchPosition', context.launchPosition);
analysis.PlotRangeTimeline(history);
analysis.PlotPhaseTimeline(history);
analysis.SummaryMetrics(history);
