function scenario = ScenarioLoader(inputArg)
%SCENARIOLOADER Load scenario from struct or file.
%   Supports .json directly. For .yaml/.yml, uses yamlread when available.

    if nargin < 1 || isempty(inputArg)
        scenario = sim.DefaultScenario();
        return;
    end

    if isstruct(inputArg)
        rawScenario = inputArg;
    else
        path = string(inputArg);
        if ~isfile(path)
            error("Scenario file not found: %s", path);
        end

        [~, ~, ext] = fileparts(path);
        ext = lower(ext);
        switch ext
            case ".json"
                rawScenario = jsondecode(fileread(path));
            case {".yaml", ".yml"}
                if exist("yamlread", "file") == 2
                    rawScenario = yamlread(path);
                else
                    error(["YAML loading requires yamlread. ", ...
                        "Use JSON input or install YAML support in your MATLAB environment."]);
                end
            otherwise
                error("Unsupported scenario extension: %s", ext);
        end
    end

    scenario = sim.DefaultScenario();

    if isfield(rawScenario, "target")
        scenario.target = localMerge(scenario.target, rawScenario.target);
    end
    if isfield(rawScenario, "surveillanceSensor")
        scenario.surveillanceSensor = localMerge(scenario.surveillanceSensor, rawScenario.surveillanceSensor);
    elseif isfield(rawScenario, "surveillance_sensor")
        scenario.surveillanceSensor = localMerge(scenario.surveillanceSensor, rawScenario.surveillance_sensor);
    end
    if isfield(rawScenario, "interceptor")
        scenario.interceptor = localMerge(scenario.interceptor, rawScenario.interceptor);
    end
    if isfield(rawScenario, "engagement")
        scenario.engagement = localMerge(scenario.engagement, rawScenario.engagement);
    end
    if isfield(rawScenario, "simulation")
        scenario.simulation = localMerge(scenario.simulation, rawScenario.simulation);
    end
end

function out = localMerge(base, update)
    out = base;
    fields = fieldnames(update);
    for i = 1:numel(fields)
        f = fields{i};
        if isstruct(update.(f)) && isfield(base, f) && isstruct(base.(f))
            out.(f) = localMerge(base.(f), update.(f));
        else
            out.(f) = update.(f);
        end
    end
end
