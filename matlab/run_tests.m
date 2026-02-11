%RUN_TESTS Execute MATLAB unit tests for the digital twin.
clear;
clc;

projectRoot = fileparts(mfilename('fullpath'));
addpath(genpath(projectRoot));

results = runtests(fullfile(projectRoot, 'tests'));

disp(table(results));
if any([results.Failed])
    error('MATLAB tests failed.');
end
