function PlotTrajectories(history, varargin)
%PLOTTRAJECTORIES Plot target, interceptor, and estimated track trajectories.
    p = inputParser;
    p.addParameter("SensorPosition", [], @(x) isempty(x) || (isnumeric(x) && numel(x) == 2));
    p.addParameter("LaunchPosition", [], @(x) isempty(x) || (isnumeric(x) && numel(x) == 2));
    p.parse(varargin{:});

    sensorPos = p.Results.SensorPosition;
    launchPos = p.Results.LaunchPosition;

    tgt = history.TargetPos;
    intc = history.InterceptorPos;
    est = history.EstTargetPos;

    figure('Color', 'w');
    hold on;
    axis equal;
    grid on;

    plot(tgt(:, 1), tgt(:, 2), 'r-', 'LineWidth', 1.8, 'DisplayName', 'Target');
    plot(intc(:, 1), intc(:, 2), 'b-', 'LineWidth', 1.8, 'DisplayName', 'Interceptor');

    valid = ~isnan(est(:, 1));
    if any(valid)
        plot(est(valid, 1), est(valid, 2), 'r--', 'LineWidth', 1.0, 'DisplayName', 'Estimated Track');
    end

    plot(tgt(1, 1), tgt(1, 2), 'ro', 'MarkerSize', 8, 'HandleVisibility', 'off');
    plot(intc(1, 1), intc(1, 2), 'bs', 'MarkerSize', 8, 'HandleVisibility', 'off');
    plot(tgt(end, 1), tgt(end, 2), 'rx', 'MarkerSize', 10, 'LineWidth', 2.0, 'HandleVisibility', 'off');
    plot(intc(end, 1), intc(end, 2), 'bx', 'MarkerSize', 10, 'LineWidth', 2.0, 'HandleVisibility', 'off');

    if ~isempty(sensorPos)
        sensorPos = reshape(sensorPos, 1, 2);
        plot(sensorPos(1), sensorPos(2), 'gd', 'MarkerSize', 8, 'DisplayName', 'Sensor');
    end
    if ~isempty(launchPos)
        launchPos = reshape(launchPos, 1, 2);
        plot(launchPos(1), launchPos(2), 'b+', 'MarkerSize', 10, 'LineWidth', 1.5, 'DisplayName', 'Launch Site');
    end

    xlabel('X (m)');
    ylabel('Y (m)');
    title('Engagement Trajectories');
    legend('Location', 'best');
    hold off;
end
