function SmithAnimator_LRight(p)
% SMITHANIMATOR_LRIGHT  L型(右)匹配电路的 Smith 圆图动态演示 (交互增强版)
% 输入 p 为结构体，包含 f, L, C1, C2, ZL, Z0

    %% 1. 初始化窗口与布局 (加大尺寸)
    fig = uifigure('Name', 'Smith圆图匹配过程演示 —— L型(右)', ...
        'Position', [100, 100, 1200, 750], ... % 【修改】窗口变大
        'Color', 'w', ...
        'CloseRequestFcn', @closeWindow); % 处理关闭事件
    
    % 主网格布局
    g = uigridlayout(fig, [1, 2]);
    g.ColumnWidth = {'2x', '1x'}; 
    
    % 左侧面板：画图
    pnlPlot = uipanel(g);
    pnlPlot.BorderType = 'none';
    pnlPlot.BackgroundColor = 'w';
    
    % 右侧面板：控制与文字
    pnlRight = uigridlayout(g, [3, 1]);
    pnlRight.RowHeight = {'1x', '3x', 'fit'}; % 标题区, 文字区, 控制区
    pnlRight.Layout.Column = 2;
    
    % --- 标题区 ---
    titleLabel = uilabel(pnlRight);
    titleLabel.FontSize = 24;
    titleLabel.FontWeight = 'bold';
    titleLabel.Text = '解题步骤详解';
    titleLabel.Layout.Row = 1;
    titleLabel.VerticalAlignment = 'bottom';
    
    % --- 文字描述区 ---
    txtLabel = uilabel(pnlRight);
    txtLabel.VerticalAlignment = 'top';
    txtLabel.WordWrap = 'on';
    txtLabel.FontSize = 16;
    txtLabel.FontName = 'Microsoft YaHei';
    txtLabel.Text = '请点击下方 [Start] 开始演示...';
    txtLabel.Layout.Row = 2;

    % --- 控制区 (按钮与滑块) ---
    pnlControls = uipanel(pnlRight);
    pnlControls.Layout.Row = 3;
    pnlControls.BackgroundColor = [0.95 0.95 0.95];
    
    % 控制区内部布局
    cg = uigridlayout(pnlControls, [2, 3]);
    cg.RowHeight = {'fit', 'fit'};
    cg.Padding = [10 10 10 10];
    
    % 速度滑块标签
    lblSpeed = uilabel(cg);
    lblSpeed.Text = '演示速度 (慢 <--> 快):';
    lblSpeed.Layout.Row = 1; 
    lblSpeed.Layout.Column = [1 3];
    
    % 速度滑块 【新增功能】
    sldSpeed = uislider(cg);
    sldSpeed.Layout.Row = 2;
    sldSpeed.Layout.Column = 1;
    sldSpeed.Limits = [1 100];
    sldSpeed.Value = 50; % 默认中等速度
    
    % 按钮组
    btnStart = uibutton(cg, 'push', 'Text', 'Start', 'FontWeight', 'bold', ...
        'ButtonPushedFcn', @onStart);
    btnStart.Layout.Row = 2; btnStart.Layout.Column = 2;
    btnStart.BackgroundColor = [0.47 0.67 0.19]; % 绿色
    btnStart.FontColor = 'w';

    btnStop = uibutton(cg, 'push', 'Text', 'Stop', ...
        'ButtonPushedFcn', @onStop);
    btnStop.Layout.Row = 2; btnStop.Layout.Column = 3;
    btnStop.BackgroundColor = [0.85 0.33 0.1]; % 红色
    btnStop.FontColor = 'w';
    btnStop.Enable = 'off';

    btnReset = uibutton(cg, 'push', 'Text', 'Reset', ...
        'ButtonPushedFcn', @onReset);
    btnReset.Layout.Row = 1; btnReset.Layout.Column = 3; % 放在上面
    
    %% 2. 预计算所有数据 (Pre-Calculation)
    w = 2 * pi * p.f;
    Z0 = p.Z0;
    
    % 辅助函数：Z -> Gamma
    z2g = @(z) (z - Z0) ./ (z + Z0);
    
    % --- 关键点计算 ---
    Z_start = p.ZL;
    
    % C2 (串联电容)
    XC2 = -1 / (w * p.C2);
    Z_mid1 = Z_start + 1j * XC2;
    
    % L (串联电感)
    XL = w * p.L;
    Z_mid2 = Z_mid1 + 1j * XL;
    
    % C1 (并联电容)
    BC1 = w * p.C1;
    
    % --- 轨迹点生成 (用于动画) ---
    steps = 100; % 增加点数使动画更丝滑
    
    % 轨迹1: Load -> C2 (蓝色)
    X_vals1 = linspace(0, XC2, steps);
    Traj1_G = z2g(Z_start + 1j * X_vals1);
    
    % 轨迹2: C2 -> L (品红色)
    X_vals2 = linspace(0, XL, steps);
    Traj2_G = z2g(Z_mid1 + 1j * X_vals2);
    
    % 轨迹3: L -> Match (绿色) - 需在导纳域计算
    Y_mid2 = 1 / Z_mid2;
    B_vals3 = linspace(0, BC1, steps);
    Traj3_G = z2g(1 ./ (Y_mid2 + 1j * B_vals3));

    % 将所有轨迹点拼成一个大的结构，方便循环
    % Phase 1: Load point (hold)
    % Phase 2: Traj1
    % Phase 3: Traj2
    % Phase 4: Traj3
    % Phase 5: End
    
    %% 3. 初始化绘图环境
    ax = axes(pnlPlot);
    try
        smithplot(ax, 'GridType', 'ZY', 'Color', [0.8 0.8 0.8]);
    catch
        title(ax, '需安装RF Toolbox才能显示背景网格');
    end
    hold(ax, 'on');
    title(ax, 'L型(右) 阻抗匹配动态演示');
    
    % 创建绘图对象 (初始为空)
    hLoad = plot(ax, nan, nan, 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
    hLine1 = plot(ax, nan, nan, 'b-', 'LineWidth', 2);
    hLine2 = plot(ax, nan, nan, 'm-', 'LineWidth', 2);
    hLine3 = plot(ax, nan, nan, 'g-', 'LineWidth', 2);
    hEnd = plot(ax, nan, nan, 'kp', 'MarkerSize', 12, 'MarkerFaceColor', 'g');
    
    % 状态变量
    state.isPlaying = false;
    state.currentPhase = 0; % 0:未开始, 1:画Load, 2:画C2, 3:画L, 4:画C1, 5:完成
    state.idx = 1;          % 当前轨迹的索引
    state.appOpen = true;   % 窗口是否开启
    
    %% 4. 主动画循环 (While Loop)
    % 这是实现暂停/继续/调速的核心
    while state.appOpen
        
        if state.isPlaying
            % 计算延迟时间：滑块值 1(最慢) -> 100(最快)
            % 延迟范围设计：0.1s (慢) ~ 0.001s (快)
            delay = 0.05 - (sldSpeed.Value / 100 * 0.049); 
            pause(delay); 
            
            updateAnimation();
        else
            % 暂停状态，低功耗等待
            pause(0.1);
        end
        
        % 保持界面响应
        drawnow limitrate;
    end
    
    %% 5. 内部逻辑函数
    
    function updateAnimation()
        switch state.currentPhase
            case 0 % 刚按下 Start，初始化
                state.currentPhase = 1;
                state.idx = 1;
                
                % 更新文字：负载
                titleLabel.Text = '步骤 1/4: 标定负载';
                txtLabel.Text = sprintf(['1. 首先在 Smith 圆图上找到归一化负载阻抗点。\n\n' ...
                             'Load Z = %.2f %+.2fj Ω\n' ...
                             '归一化 z = %.2f %+.2fj'], ...
                             real(Z_start), imag(Z_start), real(Z_start)/50, imag(Z_start)/50);
                
            case 1 % 画负载点
                g0 = z2g(Z_start);
                hLoad.XData = real(g0);
                hLoad.YData = imag(g0);
                
                % 停留一下，进入下一阶段
                if state.idx > 10 % 稍微停顿几帧
                    state.currentPhase = 2;
                    state.idx = 1;
                    
                    % 更新文字：C2
                    titleLabel.Text = '步骤 2/4: 串联电容 C2';
                    txtLabel.Text = sprintf(['2. 串联电容 C2 (%.2f pF)。\n\n' ...
                             '原理：串联电抗元件，沿着等电阻圆(Constant R Circle)移动。\n' ...
                             '电容为负电抗，沿电阻圆逆时针移动向下。\n\n' ...
                             '移动量 Xc = %.2f Ω'], ...
                             p.C2*1e12, XC2);
                else
                    state.idx = state.idx + 1;
                end
                
            case 2 % 画 C2 轨迹 (蓝色)
                if state.idx <= steps
                    hLine1.XData = real(Traj1_G(1:state.idx));
                    hLine1.YData = imag(Traj1_G(1:state.idx));
                    state.idx = state.idx + 1;
                else
                    state.currentPhase = 3;
                    state.idx = 1;
                    
                    % 更新文字：L
                    titleLabel.Text = '步骤 3/4: 串联电感 L';
                    txtLabel.Text = sprintf(['3. 串联电感 L (%.2f uH)。\n\n' ...
                             '原理：继续沿着等电阻圆移动。\n' ...
                             '电感为正电抗，顺时针移动向上。\n\n' ...
                             '目标：移动直到导纳的实部等于 1/50 S (即到达 G=1 圆上)。\n' ...
                             '移动量 XL = +%.2f Ω'], ...
                             p.L*1e6, XL);
                end
                
            case 3 % 画 L 轨迹 (品红)
                if state.idx <= steps
                    hLine2.XData = real(Traj2_G(1:state.idx));
                    hLine2.YData = imag(Traj2_G(1:state.idx));
                    state.idx = state.idx + 1;
                else
                    state.currentPhase = 4;
                    state.idx = 1;
                    
                    % 更新文字：C1
                    titleLabel.Text = '步骤 4/4: 并联电容 C1';
                    txtLabel.Text = sprintf(['4. 靠近源端并联电容 C1 (%.2f pF)。\n\n' ...
                             '原理：并联元件，沿着等电导圆(Constant G Circle)移动。\n' ...
                             '电容电纳为正 (+jB)，在导纳圆上顺时针移动。\n\n' ...
                             '最终目标：到达圆心 (50 Ω 匹配点)。'], ...
                             p.C1*1e12);
                end
                
            case 4 % 画 C1 轨迹 (绿色)
                if state.idx <= steps
                    hLine3.XData = real(Traj3_G(1:state.idx));
                    hLine3.YData = imag(Traj3_G(1:state.idx));
                    state.idx = state.idx + 1;
                else
                    state.currentPhase = 5;
                    % 画终点
                    hEnd.XData = 0; hEnd.YData = 0;
                    
                    % 更新文字：完成
                    titleLabel.Text = '匹配完成';
                    txtLabel.Text = sprintf(['恭喜！匹配网络设计完成。\n\n' ...
                             '总路径：\n' ...
                             'Load -> 串 C2 -> 串 L -> (到达 G=1 圆) -> 并 C1 -> 源端(50Ω)']);
                    
                    % 自动停止
                    state.isPlaying = false;
                    btnStart.Text = 'Finished';
                    btnStart.Enable = 'off';
                    btnStop.Enable = 'off';
                end
        end
    end

    %% 6. 回调函数 (Callbacks)
    
    function onStart(~, ~)
        state.isPlaying = true;
        btnStart.Enable = 'off';
        btnStop.Enable = 'on';
        
        % 如果是第一次开始，从头来
        if state.currentPhase == 5
             onReset();
             state.isPlaying = true;
        end
    end

    function onStop(~, ~)
        state.isPlaying = false;
        btnStart.Text = 'Continue';
        btnStart.Enable = 'on';
        btnStop.Enable = 'off';
    end

    function onReset(~, ~)
        state.isPlaying = false;
        state.currentPhase = 0;
        state.idx = 1;
        
        % 清空所有线条数据
        hLoad.XData = nan; hLoad.YData = nan;
        hLine1.XData = nan; hLine1.YData = nan;
        hLine2.XData = nan; hLine2.YData = nan;
        hLine3.XData = nan; hLine3.YData = nan;
        hEnd.XData = nan;   hEnd.YData = nan;
        
        % 重置UI
        btnStart.Text = 'Start';
        btnStart.Enable = 'on';
        btnStop.Enable = 'off';
        titleLabel.Text = '解题步骤详解';
        txtLabel.Text = '已重置。请点击 [Start] 开始演示...';
    end

    function closeWindow(~, ~)
        state.appOpen = false; % 终止while循环
        delete(fig);
    end

end