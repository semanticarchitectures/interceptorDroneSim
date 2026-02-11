function PlotPhaseTimeline(history)
%PLOTPHASETIMELINE Visualize phase timeline as a step plot.
    phases = categories(history.Phase);
    [~, idx] = ismember(string(history.Phase), phases);

    figure('Color', 'w');
    stairs(history.TimeSeconds, idx, 'LineWidth', 1.8);
    grid on;
    xlabel('Time (s)');
    ylabel('Phase');
    yticks(1:numel(phases));
    yticklabels(phases);
    title('Engagement Phase Timeline');
end
