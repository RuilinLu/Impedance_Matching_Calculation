classdef MW_V1 < matlab.apps.AppBase

    % Properties that correspond to app components
    properties (Access = public)
        UIFigure                        matlab.ui.Figure
        GridLayout                      matlab.ui.container.GridLayout
        LeftPanel                       matlab.ui.container.Panel
        Button_Quit                     matlab.ui.control.Button
        Button_About                    matlab.ui.control.Button
        Button_Z2Y                      matlab.ui.control.Button
        Button_pi_2                     matlab.ui.control.Button
        Button_pi_1                     matlab.ui.control.Button
        Button_T                        matlab.ui.control.Button
        Button_L_Left                   matlab.ui.control.Button
        Button_L_Right                  matlab.ui.control.Button
        RightPanel                      matlab.ui.container.Panel
        Button_Next                     matlab.ui.control.Button
        Button_Back                     matlab.ui.control.Button
        Button_SmithPlot                matlab.ui.control.Button
        TabGroup                        matlab.ui.container.TabGroup
        Tab_Welcome                     matlab.ui.container.Tab
        GridLayout_Welcome              matlab.ui.container.GridLayout
        Image                           matlab.ui.control.Image
        WelcomeLabel                    matlab.ui.control.Label
        Label_Member                    matlab.ui.control.Label
        Label_Designer                  matlab.ui.control.Label
        Label_Welcome                   matlab.ui.control.Label
        Image_Welcome                   matlab.ui.control.Image
        Tab_LRight_Home                 matlab.ui.container.Tab
        GridLayout5                     matlab.ui.container.GridLayout
        GridLayout12                    matlab.ui.container.GridLayout
        GridLayout13_2                  matlab.ui.container.GridLayout
        EditField_LRight_Target_Z_Im    matlab.ui.control.NumericEditField
        jEditFieldLabel                 matlab.ui.control.Label
        Button_Voltage_Max_LRight       matlab.ui.control.Button
        EditField_LRight_Cal_C2         matlab.ui.control.NumericEditField
        Z_Load_maxLabel_2               matlab.ui.control.Label
        EditField_LRight_Cal_C1         matlab.ui.control.NumericEditField
        Z_Load_minLabel_2               matlab.ui.control.Label
        C1C2Label                       matlab.ui.control.Label
        Button_LRight_Backward          matlab.ui.control.Button
        EditField_LRight_Target_Z_Real  matlab.ui.control.NumericEditField
        C1pFLabel_3                     matlab.ui.control.Label
        EditField_LRight_Set_L_2        matlab.ui.control.NumericEditField
        LHLabel                         matlab.ui.control.Label
        GridLayout13                    matlab.ui.container.GridLayout
        jLabel_8                        matlab.ui.control.Label
        jLabel_7                        matlab.ui.control.Label
        Label_2                         matlab.ui.control.Label
        Label                           matlab.ui.control.Label
        EditField_LRight_Cal_Zmax_Im    matlab.ui.control.NumericEditField
        EditField_LRight_Cal_Zmin_Im    matlab.ui.control.NumericEditField
        maxLabel                        matlab.ui.control.Label
        minLabel                        matlab.ui.control.Label
        EditField_LRight_Set_C2_max     matlab.ui.control.NumericEditField
        EditField_LRight_Set_C1_max     matlab.ui.control.NumericEditField
        EditField_LRight_Cal_Zmax_Real  matlab.ui.control.NumericEditField
        Z_Load_maxLabel                 matlab.ui.control.Label
        EditField_LRight_Cal_Zmin_Real  matlab.ui.control.NumericEditField
        Z_Load_minLabel                 matlab.ui.control.Label
        Z_LoadR_LjX_LLabel              matlab.ui.control.Label
        Button_LRight_Forward           matlab.ui.control.Button
        EditField_LRight_Set_C2_min     matlab.ui.control.NumericEditField
        C1pFLabel_2                     matlab.ui.control.Label
        EditField_LRight_Set_C1_min     matlab.ui.control.NumericEditField
        C1pFLabel                       matlab.ui.control.Label
        EditField_LRight_Set_L          matlab.ui.control.NumericEditField
        LHLabel_2                       matlab.ui.control.Label
        textbfZ_mathrmLLC_1C_2Label     matlab.ui.control.Label
        textbfLC_1C_2Z_mathrmloadLabel  matlab.ui.control.Label
        GridLayout10                    matlab.ui.container.GridLayout
        GridLayout11                    matlab.ui.container.GridLayout
        Button_Readme_L_Right           matlab.ui.control.Button
        EditField_Operat_f              matlab.ui.control.NumericEditField
        MHzLabel                        matlab.ui.control.Label
        fmathrmMHzLabel                 matlab.ui.control.Label
        Image_LRight                    matlab.ui.control.Image
        Tab_LLeft_Home                  matlab.ui.container.Tab
        GridLayout5_2                   matlab.ui.container.GridLayout
        GridLayout12_2                  matlab.ui.container.GridLayout
        GridLayout13_4                  matlab.ui.container.GridLayout
        EditField_LLeft_Target_Z_Im     matlab.ui.control.NumericEditField
        jEditFieldLabel_2               matlab.ui.control.Label
        Button_Voltage_Max_LLeft        matlab.ui.control.Button
        EditField_LLeft_Cal_C2          matlab.ui.control.NumericEditField
        Z_Load_maxLabel_4               matlab.ui.control.Label
        EditField_LLeft_Cal_C1          matlab.ui.control.NumericEditField
        Z_Load_minLabel_4               matlab.ui.control.Label
        C1C2Label_2                     matlab.ui.control.Label
        Button_LLeft_Backward           matlab.ui.control.Button
        EditField_LLeft_Target_Z_Real   matlab.ui.control.NumericEditField
        C1pFLabel_6                     matlab.ui.control.Label
        EditField_LLeft_Set_L_2         matlab.ui.control.NumericEditField
        LHLabel_4                       matlab.ui.control.Label
        GridLayout13_3                  matlab.ui.container.GridLayout
        jLabel_10                       matlab.ui.control.Label
        jLabel_9                        matlab.ui.control.Label
        Label_4                         matlab.ui.control.Label
        Label_3                         matlab.ui.control.Label
        EditField_LLeft_Cal_Zmax_Im     matlab.ui.control.NumericEditField
        EditField_LLeft_Cal_Zmin_Im     matlab.ui.control.NumericEditField
        maxLabel_2                      matlab.ui.control.Label
        minLabel_2                      matlab.ui.control.Label
        EditField_LLeft_Set_C2_max      matlab.ui.control.NumericEditField
        EditField_LLeft_Set_C1_max      matlab.ui.control.NumericEditField
        EditField_LLeft_Cal_Zmax_Real   matlab.ui.control.NumericEditField
        Z_Load_maxLabel_3               matlab.ui.control.Label
        EditField_LLeft_Cal_Zmin_Real   matlab.ui.control.NumericEditField
        Z_Load_minLabel_3               matlab.ui.control.Label
        Z_LoadR_LjX_LLabel_2            matlab.ui.control.Label
        Button_LLeft_Forward            matlab.ui.control.Button
        EditField_LLeft_Set_C2_min      matlab.ui.control.NumericEditField
        C1pFLabel_5                     matlab.ui.control.Label
        EditField_LLeft_Set_C1_min      matlab.ui.control.NumericEditField
        C1pFLabel_4                     matlab.ui.control.Label
        EditField_LLeft_Set_L_1         matlab.ui.control.NumericEditField
        LHLabel_3                       matlab.ui.control.Label
        textbfZ_mathrmLLC_1C_2Label_2   matlab.ui.control.Label
        textbfLC_1C_2Z_mathrmloadLabel_2  matlab.ui.control.Label
        GridLayout10_2                  matlab.ui.container.GridLayout
        GridLayout11_2                  matlab.ui.container.GridLayout
        Button_Readme_L_Left            matlab.ui.control.Button
        EditField_Operat_f_LLeft        matlab.ui.control.NumericEditField
        MHzLabel_3                      matlab.ui.control.Label
        fmathrmMHzLabel_2               matlab.ui.control.Label
        Image_LLeft                     matlab.ui.control.Image
        Tab_T_Home                      matlab.ui.container.Tab
        GridLayout5_3                   matlab.ui.container.GridLayout
        GridLayout12_3                  matlab.ui.container.GridLayout
        GridLayout13_6                  matlab.ui.container.GridLayout
        EditField_T_Set_C3              matlab.ui.control.NumericEditField
        Z_Load_minLabel_11              matlab.ui.control.Label
        EditField_T_Target_Z_Im         matlab.ui.control.NumericEditField
        jEditFieldLabel_3               matlab.ui.control.Label
        Button_Voltage_Max_T            matlab.ui.control.Button
        EditField_T_Cal_C2              matlab.ui.control.NumericEditField
        Z_Load_maxLabel_6               matlab.ui.control.Label
        EditField_T_Cal_C1              matlab.ui.control.NumericEditField
        Z_Load_minLabel_6               matlab.ui.control.Label
        C1C2Label_3                     matlab.ui.control.Label
        Button_T_Backward               matlab.ui.control.Button
        EditField_T_Target_Z_Real       matlab.ui.control.NumericEditField
        C1pFLabel_9                     matlab.ui.control.Label
        EditField_T_Set_L_2             matlab.ui.control.NumericEditField
        LHLabel_6                       matlab.ui.control.Label
        GridLayout13_5                  matlab.ui.container.GridLayout
        EditField_T_Set_C3_max          matlab.ui.control.NumericEditField
        Label_7                         matlab.ui.control.Label
        EditField_T_Set_C3_min          matlab.ui.control.NumericEditField
        C1pFLabel_10                    matlab.ui.control.Label
        jLabel_12                       matlab.ui.control.Label
        jLabel_11                       matlab.ui.control.Label
        Label_6                         matlab.ui.control.Label
        Label_5                         matlab.ui.control.Label
        EditField_T_Cal_Zmax_Im         matlab.ui.control.NumericEditField
        EditField_T_Cal_Zmin_Im         matlab.ui.control.NumericEditField
        maxLabel_3                      matlab.ui.control.Label
        minLabel_3                      matlab.ui.control.Label
        EditField_T_Set_C2_max          matlab.ui.control.NumericEditField
        EditField_T_Set_C1_max          matlab.ui.control.NumericEditField
        EditField_T_Cal_Zmax_Real       matlab.ui.control.NumericEditField
        Z_Load_maxLabel_5               matlab.ui.control.Label
        EditField_T_Cal_Zmin_Real       matlab.ui.control.NumericEditField
        Z_Load_minLabel_5               matlab.ui.control.Label
        Z_LoadR_LjX_LLabel_3            matlab.ui.control.Label
        Button_T_Forward                matlab.ui.control.Button
        EditField_T_Set_C2_min          matlab.ui.control.NumericEditField
        C1pFLabel_8                     matlab.ui.control.Label
        EditField_T_Set_C1_min          matlab.ui.control.NumericEditField
        C1pFLabel_7                     matlab.ui.control.Label
        EditField_T_Set_L_1             matlab.ui.control.NumericEditField
        LHLabel_5                       matlab.ui.control.Label
        textbfZ_mathrmLLC_3C_1C_2Label  matlab.ui.control.Label
        textbfLC_1C_2C_3Z_mathrmloadLabel_3  matlab.ui.control.Label
        GridLayout10_3                  matlab.ui.container.GridLayout
        GridLayout11_3                  matlab.ui.container.GridLayout
        Button_Readme_T                 matlab.ui.control.Button
        EditField_Operat_f_T            matlab.ui.control.NumericEditField
        MHzLabel_4                      matlab.ui.control.Label
        fmathrmMHzLabel_3               matlab.ui.control.Label
        Image_T                         matlab.ui.control.Image
        Tab_pi1_Home                    matlab.ui.container.Tab
        GridLayout5_6                   matlab.ui.container.GridLayout
        GridLayout12_6                  matlab.ui.container.GridLayout
        GridLayout13_12                 matlab.ui.container.GridLayout
        EditField_pi1_Set_C3_2          matlab.ui.control.NumericEditField
        Z_Load_minLabel_14              matlab.ui.control.Label
        EditField_pi1_Target_Z_Im       matlab.ui.control.NumericEditField
        jEditFieldLabel_6               matlab.ui.control.Label
        Button_Voltage_Max_pi1          matlab.ui.control.Button
        EditField_pi1_Cal_C2            matlab.ui.control.NumericEditField
        Z_Load_maxLabel_12              matlab.ui.control.Label
        EditField_pi1_Cal_C1            matlab.ui.control.NumericEditField
        Z_Load_minLabel_13              matlab.ui.control.Label
        C1C2Label_4                     matlab.ui.control.Label
        Button_pi1_Backward             matlab.ui.control.Button
        EditField_pi1_Target_Z_Real     matlab.ui.control.NumericEditField
        C1pFLabel_22                    matlab.ui.control.Label
        EditField_pi1_Set_L_2           matlab.ui.control.NumericEditField
        LHLabel_16                      matlab.ui.control.Label
        GridLayout13_11                 matlab.ui.container.GridLayout
        EditField_pi1_Set_C3_max        matlab.ui.control.NumericEditField
        Label_16                        matlab.ui.control.Label
        EditField_pi1_Set_C3_min        matlab.ui.control.NumericEditField
        C1pFLabel_21                    matlab.ui.control.Label
        jLabel_18                       matlab.ui.control.Label
        jLabel_17                       matlab.ui.control.Label
        Label_15                        matlab.ui.control.Label
        Label_14                        matlab.ui.control.Label
        EditField_pi1_Cal_Zmax_Im       matlab.ui.control.NumericEditField
        EditField_pi1_Cal_Zmin_Im       matlab.ui.control.NumericEditField
        maxLabel_6                      matlab.ui.control.Label
        minLabel_6                      matlab.ui.control.Label
        EditField_pi1_Set_C2_max        matlab.ui.control.NumericEditField
        EditField_pi1_Set_C1_max        matlab.ui.control.NumericEditField
        EditField_pi1_Cal_Zmax_Real     matlab.ui.control.NumericEditField
        Z_Load_maxLabel_11              matlab.ui.control.Label
        EditField_pi1_Cal_Zmin_Real     matlab.ui.control.NumericEditField
        Z_Load_minLabel_12              matlab.ui.control.Label
        Z_LoadR_LjX_LLabel_6            matlab.ui.control.Label
        Button_pi1_Forward              matlab.ui.control.Button
        EditField_pi1_Set_C2_min        matlab.ui.control.NumericEditField
        C1pFLabel_20                    matlab.ui.control.Label
        EditField_pi1_Set_C1_min        matlab.ui.control.NumericEditField
        C1pFLabel_19                    matlab.ui.control.Label
        EditField_pi1_Set_L             matlab.ui.control.NumericEditField
        LHLabel_15                      matlab.ui.control.Label
        textbfZ_mathrmLLC_3C_1C_2Label_2  matlab.ui.control.Label
        textbfLC_1C_2C_3Z_mathrmloadLabel_4  matlab.ui.control.Label
        GridLayout10_6                  matlab.ui.container.GridLayout
        GridLayout11_6                  matlab.ui.container.GridLayout
        Button_Readme_pi1               matlab.ui.control.Button
        EditField_Operat_f_pi1          matlab.ui.control.NumericEditField
        MHzLabel_7                      matlab.ui.control.Label
        fmathrmMHzLabel_4               matlab.ui.control.Label
        Image_pi1                       matlab.ui.control.Image
        Tab_pi2_Home                    matlab.ui.container.Tab
        GridLayout5_7                   matlab.ui.container.GridLayout
        GridLayout12_7                  matlab.ui.container.GridLayout
        GridLayout13_14                 matlab.ui.container.GridLayout
        EditField_pi2_Set_C3            matlab.ui.control.NumericEditField
        Z_Load_minLabel_17              matlab.ui.control.Label
        EditField_pi2_Target_Z_Im       matlab.ui.control.NumericEditField
        jEditFieldLabel_7               matlab.ui.control.Label
        Button_Voltage_Max_pi2          matlab.ui.control.Button
        EditField_pi2_Cal_C2            matlab.ui.control.NumericEditField
        Z_Load_maxLabel_14              matlab.ui.control.Label
        EditField_pi2_Cal_C1            matlab.ui.control.NumericEditField
        Z_Load_minLabel_16              matlab.ui.control.Label
        C1C2Label_5                     matlab.ui.control.Label
        Button_pi2_Backward             matlab.ui.control.Button
        EditField_pi2_Target_Z_Real     matlab.ui.control.NumericEditField
        C1pFLabel_26                    matlab.ui.control.Label
        EditField_pi2_Set_L_2           matlab.ui.control.NumericEditField
        LHLabel_18                      matlab.ui.control.Label
        GridLayout13_13                 matlab.ui.container.GridLayout
        EditField_pi2_Set_C3_max        matlab.ui.control.NumericEditField
        Label_19                        matlab.ui.control.Label
        EditField_pi2_Set_C3_min        matlab.ui.control.NumericEditField
        C1pFLabel_25                    matlab.ui.control.Label
        jLabel_20                       matlab.ui.control.Label
        jLabel_19                       matlab.ui.control.Label
        Label_18                        matlab.ui.control.Label
        Label_17                        matlab.ui.control.Label
        EditField_pi2_Cal_Zmax_Im       matlab.ui.control.NumericEditField
        EditField_pi2_Cal_Zmin_Im       matlab.ui.control.NumericEditField
        maxLabel_7                      matlab.ui.control.Label
        minLabel_7                      matlab.ui.control.Label
        EditField_pi2_Set_C2_max        matlab.ui.control.NumericEditField
        EditField_pi2_Set_C1_max        matlab.ui.control.NumericEditField
        EditField_pi2_Cal_Zmax_Real     matlab.ui.control.NumericEditField
        Z_Load_maxLabel_13              matlab.ui.control.Label
        EditField_pi2_Cal_Zmin_Real     matlab.ui.control.NumericEditField
        Z_Load_minLabel_15              matlab.ui.control.Label
        Z_LoadR_LjX_LLabel_7            matlab.ui.control.Label
        Button_pi2_Forward              matlab.ui.control.Button
        EditField_pi2_Set_C2_min        matlab.ui.control.NumericEditField
        C1pFLabel_24                    matlab.ui.control.Label
        EditField_pi2_Set_C1_min        matlab.ui.control.NumericEditField
        C1pFLabel_23                    matlab.ui.control.Label
        EditField_pi2_Set_L             matlab.ui.control.NumericEditField
        LHLabel_17                      matlab.ui.control.Label
        textbfZ_mathrmLLC_3C_1C_2Label_3  matlab.ui.control.Label
        textbfLC_1C_2C_3Z_mathrmloadLabel_5  matlab.ui.control.Label
        GridLayout10_7                  matlab.ui.container.GridLayout
        GridLayout11_7                  matlab.ui.container.GridLayout
        Button_Readme_pi2               matlab.ui.control.Button
        EditField_Operat_f_pi2          matlab.ui.control.NumericEditField
        MHzLabel_8                      matlab.ui.control.Label
        fmathrmMHzLabel_5               matlab.ui.control.Label
        Image_pi2                       matlab.ui.control.Image
        Tab_Z2Y_Home                    matlab.ui.container.Tab
        GridLayout2_2                   matlab.ui.container.GridLayout
        itRitGitG2itB2itXitBitG2itB2Label  matlab.ui.control.Label
        GridLayout3_9                   matlab.ui.container.GridLayout
        ZLabel_5                        matlab.ui.control.Label
        EditField_Z_X_output            matlab.ui.control.NumericEditField
        EditField_Z_R_output            matlab.ui.control.NumericEditField
        jLabel_6                        matlab.ui.control.Label
        GridLayout3_7                   matlab.ui.container.GridLayout
        YLabel_2                        matlab.ui.control.Label
        EditField_Y_B_output            matlab.ui.control.NumericEditField
        EditField_Y_G_output            matlab.ui.control.NumericEditField
        jLabel_4                        matlab.ui.control.Label
        GridLayout3_5                   matlab.ui.container.GridLayout
        YLabel                          matlab.ui.control.Label
        EditField_Y_B                   matlab.ui.control.NumericEditField
        EditField_Y_G                   matlab.ui.control.NumericEditField
        jLabel_2                        matlab.ui.control.Label
        itGitRitR2itX2itBitXitR2itX2Label  matlab.ui.control.Label
        itYitGjitBitGitBLabel           matlab.ui.control.Label
        itZitRjitXitRitXLabel           matlab.ui.control.Label
        Button_y2z                      matlab.ui.control.Button
        itZ1itYLabel                    matlab.ui.control.Label
        itY1itZLabel                    matlab.ui.control.Label
        Button_z2y                      matlab.ui.control.Button
        GridLayout3_3                   matlab.ui.container.GridLayout
        ZLabel                          matlab.ui.control.Label
        EditField_Z_X                   matlab.ui.control.NumericEditField
        EditField_Z_R                   matlab.ui.control.NumericEditField
        jLabel                          matlab.ui.control.Label
        Tab_About_Home                  matlab.ui.container.Tab
        GridLayout_About                matlab.ui.container.GridLayout
        SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label  matlab.ui.control.Label
        Introduction2                   matlab.ui.control.Label
        Introduction1                   matlab.ui.control.Label
        Label_About                     matlab.ui.control.Label
    end

    % Properties that correspond to apps with auto-reflow
    properties (Access = private)
        onePanelWidth = 576;
    end

    
    properties (Access = private)
        ReadmeApp_L_Right       % 用于存储L右型说明书窗口的句柄
        ReadmeApp_L_Left        % 用于存储L左型说明书窗口的句柄
        ReadmeApp_T             % T型电路说明书句柄
        ReadmeApp_pi1           % pi1型电路说明书句柄
        ReadmeApp_pi2           % pi2型电路说明书句柄
        VoltageApp              %通用耐压计算窗口句柄
        CurrentActiveTab matlab.ui.container.Tab % 用于记录当前合法的Tab
        
        
        
    end
    
    methods (Access = public)
        
        % ========================================================
        % 【在这里粘贴 unlockAllButtons 函数】
        % 确保它是一个独立的块，不要嵌套在其他 function end 里面
        % ========================================================
        
        function unlockAllButtons(app)
            % 1. 恢复左侧
            app.Button_L_Right.Enable = 'on';
            app.Button_L_Left.Enable = 'on';
            app.Button_T.Enable = 'on';
            app.Button_pi_1.Enable = 'on';
            app.Button_pi_2.Enable = 'on';
            app.Button_Z2Y.Enable = 'on';
            app.Button_About.Enable = 'on';
            % 2. 回到 Welcome 页面时，禁用底部功能按钮
            app.Button_Next.Enable = 'off';
            app.Button_SmithPlot.Enable = 'off';
            app.Button_Back.Enable = 'off';
        end
    end
    
    methods (Access = private)
        
       % Tab组的选择改变回调（实现“禁止点击标题切换”）
        function TabGroupSelectionChanged(app, event)
            % 1. 获取当前点击的 Tab
            selectedTab = app.TabGroup.SelectedTab;
            
            % 2. 【关键一步】承认这次切换，更新记录变量
            app.CurrentActiveTab = selectedTab; 
            
            % 3. 根据所在的页面，执行强制的界面状态同步
            if selectedTab == app.Tab_Welcome
                % === 如果回到了 Welcome 页面 ===
                % 解锁左侧按钮 (直接调用你写好的 public 函数)
                unlockAllButtons(app);
                
                % 禁用底部功能按钮
                app.Button_Next.Enable = 'off';
                app.Button_SmithPlot.Enable = 'off';
                app.Button_Back.Enable = 'off';
                
            else
                % === 如果进入了任何功能页面 (L型, T型, Z2Y等) ===
                
                % A. 【强制锁死左侧导航栏】(复制了你按钮里的逻辑)
                app.Button_L_Right.Enable = 'off';
                app.Button_L_Left.Enable = 'off';
                app.Button_T.Enable = 'off';
                app.Button_pi_1.Enable = 'off';
                app.Button_pi_2.Enable = 'off';
                app.Button_Z2Y.Enable = 'off';
                app.Button_About.Enable = 'off';
                
                % B. 设置底部 Back 按钮
                app.Button_Back.Enable = 'on';
                
                % C. 设置 Smith 圆图按钮 (About页和计算页没有圆图)
                if selectedTab == app.Tab_Z2Y_Home || selectedTab == app.Tab_About_Home
                     app.Button_SmithPlot.Enable = 'off';
                else
                     app.Button_SmithPlot.Enable = 'on';
                end
                
                % D. 设置 Next 按钮 (默认进入新页面时 Next 为关闭，除非你有额外逻辑)
                % 这里为了安全，统一先设为 off，和你之前的逻辑保持一致
                app.Button_Next.Enable = 'off'; 
            end
        end

        
        
        function changeTab(app, targetTab)
            % 1. 更新允许的Tab
            app.CurrentActiveTab = targetTab;
            % 2. 执行切换
            app.TabGroup.SelectedTab = targetTab;
            
            % 3. 【核心需求】集中管理 Next 按钮的禁用逻辑
            if targetTab == app.Tab_Welcome
                app.Button_Next.Enable = 'off'; % Welcome页禁用
            elseif targetTab == app.Tab_LRight_Home
                app.Button_Next.Enable = 'off'; % L型(右)页禁用
            elseif targetTab == app.Tab_Z2Y_Home
                app.Button_Next.Enable = 'off'; % 计算页保持禁用
            elseif targetTab == app.Tab_About_Home
                app.Button_Next.Enable = 'off'; % About页保持禁用
            elseif targetTab == app.Tab_LLeft_Home
                app.Button_Next.Enable = 'off'; % L型(左)页保持禁用
            elseif targetTab == app.Tab_T_Home
                app.Button_Next.Enable = 'off'; % T型页保持禁用
            elseif targetTab == app.Tab_pi1_Home
                app.Button_Next.Enable = 'off'; % pi1型页保持禁用
            elseif targetTab == app.Tab_pi2_Home
                app.Button_Next.Enable = 'off'; % pi2型页保持禁用
            else
                % 其他页面（T, pi1, pi2等）默认开启
                app.Button_Next.Enable = 'on';
            end
        end
        
        function Z_L = calculate_impedance_pi1(app,w, Z0, L, C1, C2, C3)
            % 步骤 1: 源端并联 C3
            Y_S = 1/Z0 + 1j*w*C3;
            Z_S_eff = 1/Y_S;
            
            % 步骤 2: 串联臂 (L + C2)
            Z_branch = 1j*w*L + 1/(1j*w*C2);
            Z_before_C1 = Z_S_eff + Z_branch;
            
            % 步骤 3: 负载端并联 C1
            % 从负载端看进去的导纳 Y_in = 1/Z_before_C1 + jwC1
            Y_in = 1/Z_before_C1 + 1j*w*C1;
            Z_in = 1/Y_in;
            
            % 匹配条件：负载应为输入阻抗的共轭
            Z_L = conj(Z_in);
        end
    end
    

    % Callbacks that handle component events
    methods (Access = private)

        % Code that executes after component creation
        function startupFcn(app)
            % 1. 禁用所有 Tab 页的交互 (禁止鼠标点击顶部切换)
            %app.Tab_LRight_Home.Enable = 'off';
            %app.Tab_LLeft_Home.Enable = 'off';
            %app.Tab_T_Home.Enable = 'off';
            %app.Tab_pi1_Home.Enable = 'off';
            %app.Tab_pi2_Home.Enable = 'off';
            %app.Tab_Z2Y_Home.Enable = 'off';
            %app.Tab_About_Home.Enable = 'off';
            % 2. 初始化“当前允许的Tab”为 Welcome
            app.CurrentActiveTab = app.Tab_Welcome;
            app.TabGroup.SelectedTab = app.Tab_Welcome;

            % 3. 注册Tab组的切换监听器（实现“禁止点击”）
            app.TabGroup.SelectionChangedFcn = createCallbackFcn(app, @TabGroupSelectionChanged, true);

            % 4. 启动时禁用 Next, Smith 和 Back 按钮
            app.Button_Next.Enable = 'off'; % 【需求】Welcome页禁用Next
            app.Button_SmithPlot.Enable = 'off';
            app.Button_Back.Enable = 'off';
        end

        % Button pushed function: Button_L_Right
        function Button_L_RightPushed(app, event)
            % 1. 使用新函数切换到 L型(右)
            % (changeTab 内部会自动禁用 Next 按钮，满足你的需求)
            changeTab(app, app.Tab_LRight_Home);
    
            % 2. 【封锁逻辑】禁用左侧导航栏 (除 Quit 外)
            app.Button_L_Right.Enable = 'off';
            app.Button_L_Left.Enable = 'off';
            app.Button_T.Enable = 'off';
            app.Button_pi_1.Enable = 'off';
            app.Button_pi_2.Enable = 'off';
            app.Button_Z2Y.Enable = 'off';
            app.Button_About.Enable = 'off';
        
            % 3. 激活底部功能按钮 (Next由changeTab控制，这里只需处理其他)
            app.Button_SmithPlot.Enable = 'on';
            app.Button_Back.Enable = 'on';
        end

        % Button pushed function: Button_L_Left
        function Button_L_LeftPushed(app, event)
            % 1. 使用新函数切换到 L型(左)
            % (changeTab 内部会自动禁用 Next 按钮，满足你的需求)
            changeTab(app, app.Tab_LLeft_Home);
    
            % 2. 【封锁逻辑】禁用左侧导航栏 (除 Quit 外)
            app.Button_L_Right.Enable = 'off';
            app.Button_L_Left.Enable = 'off';
            app.Button_T.Enable = 'off';
            app.Button_pi_1.Enable = 'off';
            app.Button_pi_2.Enable = 'off';
            app.Button_Z2Y.Enable = 'off';
            app.Button_About.Enable = 'off';
        
            % 3. 激活底部功能按钮 (Next由changeTab控制，这里只需处理其他)
            app.Button_SmithPlot.Enable = 'on';
            app.Button_Back.Enable = 'on';
        end

        % Button pushed function: Button_T
        function Button_TPushed(app, event)
            % 1. 使用新函数切换到 T型
            % (changeTab 内部会自动禁用 Next 按钮，满足你的需求)
            changeTab(app, app.Tab_T_Home);
    
            % 2. 【封锁逻辑】禁用左侧导航栏 (除 Quit 外)
            app.Button_L_Right.Enable = 'off';
            app.Button_L_Left.Enable = 'off';
            app.Button_T.Enable = 'off';
            app.Button_pi_1.Enable = 'off';
            app.Button_pi_2.Enable = 'off';
            app.Button_Z2Y.Enable = 'off';
            app.Button_About.Enable = 'off';
        
            % 3. 激活底部功能按钮 (Next由changeTab控制，这里只需处理其他)
            app.Button_SmithPlot.Enable = 'on';
            app.Button_Back.Enable = 'on';
        end

        % Button pushed function: Button_pi_1
        function Button_pi_1Pushed(app, event)
            % 1. 使用新函数切换到 pi型电路 I 
            % (changeTab 内部会自动禁用 Next 按钮，满足你的需求)
            changeTab(app, app.Tab_pi1_Home);
    
            % 2. 【封锁逻辑】禁用左侧导航栏 (除 Quit 外)
            app.Button_L_Right.Enable = 'off';
            app.Button_L_Left.Enable = 'off';
            app.Button_T.Enable = 'off';
            app.Button_pi_1.Enable = 'off';
            app.Button_pi_2.Enable = 'off';
            app.Button_Z2Y.Enable = 'off';
            app.Button_About.Enable = 'off';
        
            % 3. 激活底部功能按钮 (Next由changeTab控制，这里只需处理其他)
            app.Button_SmithPlot.Enable = 'on';
            app.Button_Back.Enable = 'on';
        end

        % Button pushed function: Button_pi_2
        function Button_pi_2Pushed(app, event)
            % 1. 使用新函数切换到 pi型电路 II 
            % (changeTab 内部会自动禁用 Next 按钮，满足你的需求)
            changeTab(app, app.Tab_pi2_Home);
    
            % 2. 【封锁逻辑】禁用左侧导航栏 (除 Quit 外)
            app.Button_L_Right.Enable = 'off';
            app.Button_L_Left.Enable = 'off';
            app.Button_T.Enable = 'off';
            app.Button_pi_1.Enable = 'off';
            app.Button_pi_2.Enable = 'off';
            app.Button_Z2Y.Enable = 'off';
            app.Button_About.Enable = 'off';
        
            % 3. 激活底部功能按钮 (Next由changeTab控制，这里只需处理其他)
            app.Button_SmithPlot.Enable = 'on';
            app.Button_Back.Enable = 'on';
        end

        % Button pushed function: Button_Z2Y
        function Button_Z2YPushed(app, event)
            % 1. 使用新函数切换到 阻抗导纳计算
            % (changeTab 内部会自动禁用 Next 按钮，满足你的需求)
            changeTab(app, app.Tab_Z2Y_Home);
            
            % 2. 【封锁逻辑】禁用左侧导航栏 (除 Quit 外)
            app.Button_L_Right.Enable = 'off';
            app.Button_L_Left.Enable = 'off';
            app.Button_T.Enable = 'off';
            app.Button_pi_1.Enable = 'off';
            app.Button_pi_2.Enable = 'off';
            app.Button_Z2Y.Enable = 'off'; % 自己也禁用
            app.Button_About.Enable = 'off';
            
            % 3. 激活底部功能按钮 (Next由changeTab控制，这里只需处理其他)
            app.Button_SmithPlot.Enable = 'off';
            app.Button_Back.Enable = 'on';
            % Back 和 Quit 保持开启 ('on'),next关闭
        end

        % Button pushed function: Button_About
        function Button_AboutPushed(app, event)
            % 1. 使用新函数切换到  About 
            % (changeTab 内部会自动禁用 Next 按钮，满足你的需求)
            changeTab(app, app.Tab_About_Home);
            
            % 2. 【关键】禁用所有不相关的按钮 (实现“没有任何反应”)
            % 禁用左侧导航栏
            app.Button_L_Right.Enable = 'off';
            app.Button_L_Left.Enable = 'off';
            app.Button_T.Enable = 'off';
            app.Button_pi_1.Enable = 'off';
            app.Button_pi_2.Enable = 'off';
            app.Button_Z2Y.Enable = 'off';
            app.Button_About.Enable = 'off';

            % 3. 激活底部功能按钮 (Next由changeTab控制，这里只需处理其他)
            app.Button_SmithPlot.Enable = 'off';
            app.Button_Back.Enable = 'on';
            % Back 和 Quit 保持开启 ('on'),next关闭
        end

        % Button pushed function: Button_Quit
        function Button_QuitPushed(app, event)
            % 删除整个 UIFigure，即关闭程序
            delete(app.UIFigure);
        end

        % Button pushed function: Button_Back
        function Button_BackPushed(app, event)
            % 使用 switch 判断当前所在的 Tab
            switch app.TabGroup.SelectedTab
                % === 情况 1: 如果是从 About 页面返回 ===
                case app.Tab_About_Home
                    % 1. 解除所有被禁用按钮
                    unlockAllButtons(app);
                    % 2. 返回 Welcome 页面
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                % === 情况 2: 从 阻抗导纳计算 页面返回 ===
                case app.Tab_Z2Y_Home
                    % 1. 解除所有被禁用按钮
                    unlockAllButtons(app);
                    % 2. 返回 Welcome 页面
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                % === 情况 3: 从 L型(右) 页面返回 ===
                case app.Tab_LRight_Home
                    % 1. 解除所有被禁用按钮
                    unlockAllButtons(app);
                    % 2. 返回 Welcome 页面
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                % === 情况 4: 从 L型(左) 页面返回 ===
                case app.Tab_LLeft_Home
                    % 1. 解除所有被禁用按钮
                    unlockAllButtons(app);
                    % 2. 返回 Welcome 页面
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                % === 情况 5: 从 T型 页面返回 ===
                case app.Tab_T_Home
                    % 1. 解除所有被禁用按钮
                    unlockAllButtons(app);
                    % 2. 返回 Welcome 页面
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                % === 情况 6: 从 pi1型 页面返回 ===
                case app.Tab_pi1_Home
                    % 1. 解除所有被禁用按钮
                    unlockAllButtons(app);
                    % 2. 返回 Welcome 页面
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                % === 情况 7: 从 pi2型 页面返回 ===
                case app.Tab_pi2_Home
                    % 1. 解除所有被禁用按钮
                    unlockAllButtons(app);
                    % 2. 返回 Welcome 页面
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                % === 情况 8: 其他所有页面 (默认行为) ===
                otherwise
                    % 不需要解锁，直接返回 Welcome 即可
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
            end
        end

        % Button pushed function: Button_Next
        function Button_NextPushed(app, event)
            % 判断当前在哪里，决定下一步去哪里
            switch app.TabGroup.SelectedTab
                
                % 1. 从 欢迎页 -> L型(右)
                case app.Tab_Welcome
                    app.TabGroup.SelectedTab = app.Tab_LRight_Home;
                    
                % 2. 从 L型(右) -> L型(左)
                case app.Tab_LRight_Home
                    app.TabGroup.SelectedTab = app.Tab_LLeft_Home;
                    
                % 3. 从 L型(左) -> T型
                case app.Tab_LLeft_Home
                    app.TabGroup.SelectedTab = app.Tab_T_Home;
                    
                % 4. 从 T型 -> pi型 I
                case app.Tab_T_Home
                    app.TabGroup.SelectedTab = app.Tab_pi1_Home;
                    
                % 5. 从 pi型 I -> pi型 II
                case app.Tab_pi1_Home
                    app.TabGroup.SelectedTab = app.Tab_pi2_Home;
                    
                % 6. 从 pi型 II -> 阻抗导纳计算
                case app.Tab_pi2_Home
                    app.TabGroup.SelectedTab = app.Tab_Z2Y_Home;
                    
                % 7. 从 阻抗导纳计算 -> (这里您可以选择回到首页，或者停住)
                case app.Tab_Z2Y_Home
                    % 示例：循环回到 Welcome
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
                    
                % 8. 如果在 About 页面 (理论上Next按钮是灰色的，点不了，但为了代码健壮性可以写上)
                case app.Tab_About_Home
                    % Do nothing or go back
                    
                otherwise
                    % 防止意外情况，默认回首页
                    app.TabGroup.SelectedTab = app.Tab_Welcome;
            end
        end

        % Button pushed function: Button_z2y
        function Button_z2yPushed(app, event)
            % 1. 获取输入的 R 和 X
            R = app.EditField_Z_R.Value;
            X = app.EditField_Z_X.Value;
            
            % 2. 计算分母 (模的平方)
            denominator = R^2 + X^2;
            
            % 3. 错误检查：防止除以 0
            if denominator == 0
                uialert(app.UIFigure, '阻抗模不能为0 (短路状态无法计算导纳)', '计算错误');
                return;
            end
            
            % 4. 计算导纳 G 和 B (注意 B 的负号)
            G_val = R / denominator;
            B_val = -X / denominator;
            
            % 5. 将结果写入下方的“只读输出框”
            app.EditField_Y_G_output.Value = G_val;
            app.EditField_Y_B_output.Value = B_val;
        end

        % Button pushed function: Button_y2z
        function Button_y2zPushed(app, event)
            % 1. 获取输入的 G 和 B
            G = app.EditField_Y_G.Value;
            B = app.EditField_Y_B.Value;
            
            % 2. 计算分母
            denominator = G^2 + B^2;
            
            % 3. 错误检查
            if denominator == 0
                uialert(app.UIFigure, '导纳模不能为0 (开路状态无法计算阻抗)', '计算错误');
                return;
            end
            
            % 4. 计算阻抗 R 和 X (注意 X 的负号)
            R_val = G / denominator;
            X_val = -B / denominator;
            
            % 5. 将结果写入下方的“只读输出框”
            app.EditField_Z_R_output.Value = R_val;
            app.EditField_Z_X_output.Value = X_val;
        end

        % Button pushed function: Button_Readme_L_Right
        function Button_Readme_L_RightPushed(app, event)
            % ---------------------------------------------------------
            % 1. 【路径修复】确保 MATLAB 能找到子文件夹里的文件
            % 获取当前主程序(MW_V1)所在的文件夹路径
            currentPath = fileparts(mfilename('fullpath')); 
            % 拼接出说明书所在的子文件夹路径
            readmePath = fullfile(currentPath, 'Readme');
            % 将该路径加入 MATLAB 搜索路径 (否则会报错找不到文件)
            addpath(readmePath);
            % ---------------------------------------------------------
            % 2. 检查窗口是否已经存在且有效
            % 注意：这里把 app.ReadmeApp 改成了您的 app.ReadmeApp_L_Right
            if isempty(app.ReadmeApp_L_Right) || ~isvalid(app.ReadmeApp_L_Right)
                
                % 3. 创建新窗口并赋值给属性“抓住”它
                app.ReadmeApp_L_Right = Readme_L_Right;
                
            else
                % 4. 如果已经存在，直接带到最前面
                figure(app.ReadmeApp_L_Right.UIFigure);
            end

            
        end

        % Button pushed function: Button_LRight_Forward
        function Button_LRight_ForwardPushed(app, event)
           % 1. 获取输入参数
            f_MHz = app.EditField_Operat_f.Value;
            L_uH = app.EditField_LRight_Set_L.Value;
            
            % 获取范围
            C1_min_pF = app.EditField_LRight_Set_C1_min.Value;
            C1_max_pF = app.EditField_LRight_Set_C1_max.Value;
            C2_min_pF = app.EditField_LRight_Set_C2_min.Value;
            C2_max_pF = app.EditField_LRight_Set_C2_max.Value;
            
            % 2. 单位换算与防错处理
            w = 2 * pi * f_MHz * 1e6;
            L = L_uH * 1e-6;
            
            % 防止电容为0导致除以零错误，设置一个极小物理值 (例如 0.01pF)
            min_cap_limit = 0.01; 
            
            % 确保 max >= min，且不为0
            C1_min = max(min(C1_min_pF, C1_max_pF), min_cap_limit) * 1e-12;
            C1_max = max(max(C1_min_pF, C1_max_pF), min_cap_limit) * 1e-12;
            
            C2_min = max(min(C2_min_pF, C2_max_pF), min_cap_limit) * 1e-12;
            C2_max = max(max(C2_min_pF, C2_max_pF), min_cap_limit) * 1e-12;
            
            % 3. 【核心改进】网格扫描法
            % 生成 C1 和 C2 的扫描向量 (各取 50 个点，足够平滑)
            steps = 50; 
            c1_vec = linspace(C1_min, C1_max, steps);
            c2_vec = linspace(C2_min, C2_max, steps);
            
            % 生成网格 [C1_grid, C2_grid]
            [C1_grid, C2_grid] = meshgrid(c1_vec, c2_vec);
            
            % 4. 矩阵化计算阻抗 (公式与之前相同，但现在一次算 2500 个点)
            % Z_Load = Z_source_parallel_eq - Z_series_branch
            % Term1: 源端并联 C1 后的等效阻抗
            Z_src_eq = 1 ./ (1/50 - 1j .* w .* C1_grid);
            
            % Term2: 串联支路阻抗 (L + C2)
            % 注意：电容 C2 的阻抗是 -j/(wC2)，减去它等于加上 j/(wC2)
            Z_series = 1j .* w .* L - 1j ./ (w .* C2_grid);
            
            % 总负载阻抗
            Z_Load_Matrix = Z_src_eq - Z_series;
            
            % 5. 提取极值 (实部和虚部分别找最大最小)
            R_vals = real(Z_Load_Matrix);
            X_vals = imag(Z_Load_Matrix);
            
            R_min = min(R_vals(:));
            R_max = max(R_vals(:));
            X_min = min(X_vals(:));
            X_max = max(X_vals(:));
            
            % 6. 显示结果
            app.EditField_LRight_Cal_Zmin_Real.Value = R_min;
            app.EditField_LRight_Cal_Zmin_Im.Value = X_min;
            
            app.EditField_LRight_Cal_Zmax_Real.Value = R_max;
            app.EditField_LRight_Cal_Zmax_Im.Value = X_max;
        end

        % Button pushed function: Button_LRight_Backward
        function Button_LRight_BackwardPushed(app, event)
            % 1. 获取输入参数
            f_MHz = app.EditField_Operat_f.Value;
            L_uH = app.EditField_LRight_Set_L_2.Value; % 右侧选定的电感L
            
            % 【关键修改】分别获取目标负载阻抗的实部和虚部
            % 使用您图片1中显示的变量名
            R_L = app.EditField_LRight_Target_Z_Real.Value; 
            X_L = app.EditField_LRight_Target_Z_Im.Value;   
            
            % 2. 基础参数检查
            if R_L >= 50
                uialert(app.UIFigure, '负载实部必须小于 50 欧姆才能使用此电路匹配！', '参数错误');
                return;
            end
            if R_L <= 0
                uialert(app.UIFigure, '负载实部必须大于 0！', '参数错误');
                return;
            end
            
            % 3. 单位换算
            w = 2 * pi * f_MHz * 1e6;
            L = L_uH * 1e-6;
            
            % 4. 核心计算算法
            % ----------------------------------------------------
            % 4.1 计算品质因数 Q
            Q = sqrt(50 / R_L - 1);
            
            % 4.2 计算 C1 (源端并联电容)
            C1_val = Q / (50 * w);
            
            % 4.3 计算 C2 (负载端串联电容)
            % 需要的总串联电抗 (感性)
            X_total_needed = Q * R_L; 
            
            % 求解 C2: 1/(w*C2) = w*L + X_L - X_total_needed
            denom = w * L + X_L - X_total_needed;
            
            % 4.4 检查无解情况
            if denom <= 0
                uialert(app.UIFigure, '无法匹配：选定的电感 L 值太小，或者负载容性过大。请尝试增大 L 值。', '无解');
                app.EditField_LRight_Cal_C1.Value = 0;
                app.EditField_LRight_Cal_C2.Value = 0;
                return;
            else
                C2_val = 1 / (w * denom);
            end
            
            % 5. 结果显示 (换算为 pF)
            app.EditField_LRight_Cal_C1.Value = C1_val * 1e12;
            app.EditField_LRight_Cal_C2.Value = C2_val * 1e12;
        end

        % Button pushed function: Button_Voltage_Max_LLeft, 
        % ...and 4 other components
        function Button_Voltage_Max_Pushed(app, event)
            % --- 1. 预定义变量 ---
            % 初始化变量，防止未赋值报错
            f = 0; 
            L = 0; C1 = 0; C2 = 0; C3 = 0;
            Z_Real = 0; Z_Im = 0;
            Type = 0;
        
            % --- 2. 根据当前选中的 Tab 对象进行判断 ---
            % 【关键修改】这里直接 switch 当前选中的 Tab 组件对象，而不是它的 Title 字符串
            switch app.TabGroup.SelectedTab 
                
                case app.Tab_LRight_Home  % <--- 对应图片中的第1个变量名
                    % ================= 情况1：L型(右) =================
                    % 1.1 获取该页面特定的频率
                    f = app.EditField_Operat_f.Value; 
                    
                    % 1.2 获取 L, C1, C2 (C3置0)
                    L = app.EditField_LRight_Set_L_2.Value;
                    C1 = app.EditField_LRight_Cal_C1.Value;
                    C2 = app.EditField_LRight_Cal_C2.Value;
                    C3 = 0; 
                    
                    % 1.3 获取负载实部和虚部
                    Z_Real = app.EditField_LRight_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_LRight_Target_Z_Im.Value;
                    
                    % 1.4 标记类型
                    Type = 1; 
        
                case app.Tab_LLeft_Home   % <--- 对应图片中的第2个变量名
                    % ================= 情况2：L型(左) =================
                    % 拓扑：源 -> [串联 L + C2] -> [并联 C1] -> 负载
                    
                    % 1.1 获取该页面特定的频率 (注意控件名后缀 _LLeft)
                    f = app.EditField_Operat_f_LLeft.Value; 
                    
                    % 1.2 获取 L, C1, C2 (C3置0)
                    % 注意：使用“反向计算”区域的控件值
                    L = app.EditField_LLeft_Set_L_2.Value;
                    C1 = app.EditField_LLeft_Cal_C1.Value;
                    C2 = app.EditField_LLeft_Cal_C2.Value;
                    C3 = 0; 
                    
                    % 1.3 获取负载实部和虚部
                    Z_Real = app.EditField_LLeft_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_LLeft_Target_Z_Im.Value;
                    
                    % 1.4 标记类型 (Type 2 代表 L型左)
                    Type = 2;
                    
                case app.Tab_T_Home       % <--- 情况3：T型
                    % ================= 情况3：T型 =================
                    % 拓扑：源 -> [串 C3] -> [Node] -> [串 C1] -> 负载
                    %                         |
                    %                      [并 L+C2] -> 地
                    
                    % 1.1 获取频率
                    f = app.EditField_Operat_f_T.Value; 
                    
                    % 1.2 获取元件值 (反向计算结果)
                    L  = app.EditField_T_Set_L_2.Value; % 选定的L
                    C1 = app.EditField_T_Cal_C1.Value;   % 计算出的C1
                    C2 = app.EditField_T_Cal_C2.Value;   % 计算出的C2
                    C3 = app.EditField_T_Set_C3.Value;   % 【您指定的】选定电容C3
                    
                    % 1.3 获取目标负载
                    Z_Real = app.EditField_T_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_T_Target_Z_Im.Value;
                    
                    % 1.4 标记类型为 3
                    Type = 3;
                    
                case app.Tab_pi1_Home     % <--- 对应图片中的第4个变量名
                    % ================= 情况4：PiⅠ型 =================
                    % 拓扑：C-LC-C 结构
                    % 源端并联 C3，中间串联 L+C2，负载端并联 C1
                    
                    % 1.1 获取 Pi1 页面特定的频率
                    f = app.EditField_Operat_f_pi1.Value; 
                    
                    % 1.2 获取元件值
                    % 注意：在 Pi1 反向计算中，L 和 C3 是“设置值”(后缀通常是_2)，C1 和 C2 是“计算值”
                    L  = app.EditField_pi1_Set_L_2.Value;   % 设置的 L
                    C3 = app.EditField_pi1_Set_C3_2.Value;  % 设置的 C3
                    C1 = app.EditField_pi1_Cal_C1.Value;    % 计算出的 C1
                    C2 = app.EditField_pi1_Cal_C2.Value;    % 计算出的 C2
                    
                    % 1.3 获取目标负载
                    Z_Real = app.EditField_pi1_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_pi1_Target_Z_Im.Value;
                    
                    % 1.4 标记类型为 4
                    Type = 4;
                    
                case app.Tab_pi2_Home     % <--- 对应图片中的第5个变量名
                    % ================= 情况5：PiⅡ型 =================
                    % 拓扑：源(50Ω) || C1 -> 串联(L+C2) -> 并联(C3 || Z_Load)
                    % 特点：固定负载端电容 C3，调节源端 C1 和中间 C2
                    
                    % 1.1 获取 Pi2 页面频率
                    f = app.EditField_Operat_f_pi2.Value; 
                    
                    % 1.2 获取元件值
                    % L 和 C3 是“设置值” (已知量)
                    L  = app.EditField_pi2_Set_L_2.Value;   
                    C3 = app.EditField_pi2_Set_C3.Value;    
                    
                    % C1 和 C2 是“计算值” (待求量)
                    C1 = app.EditField_pi2_Cal_C1.Value;    
                    C2 = app.EditField_pi2_Cal_C2.Value;    
                    
                    % 1.3 获取目标负载
                    Z_Real = app.EditField_pi2_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_pi2_Target_Z_Im.Value;
                    
                    % 1.4 标记类型为 5
                    Type = 5;
                    
                otherwise
                    % 这是一个防御性编程，防止选中了意料之外的Tab
                    uialert(app.UIFigure, '当前选中的页面未配置电压计算功能！', '配置错误');
                    return;
            end
            
            % --- 3. 数据检查 (通用逻辑) ---
            % 检查是否已经计算出电容值 (防止全为0的情况)
            if C1 == 0 && C2 == 0 && C3 == 0
                uialert(app.UIFigure, '参数数据缺失或为0，请先进行“反向计算”！', '错误');
                return;
            end
            
            % --- 4. 路径设置 (通用) ---
            currentPath = fileparts(mfilename('fullpath')); 
            voltagePath = fullfile(currentPath, 'Voltage');
            addpath(voltagePath);
            
            % --- 5. 打开窗口并传递参数 (通用) ---
            % 此时 switch 内部已经把 f, L, C1...Type 都赋值好了
            if isempty(app.VoltageApp) || ~isvalid(app.VoltageApp)
                app.VoltageApp = Component_Voltage_All(f, L, C1, C2, C3, Z_Real, Z_Im, Type);
            else
                delete(app.VoltageApp);
                app.VoltageApp = Component_Voltage_All(f, L, C1, C2, C3, Z_Real, Z_Im, Type);
            end
        end

        % Button pushed function: Button_SmithPlot
        function Button_SmithPlotPushed(app, event)
            % -------------------------------------------------------------
            % 1. 【路径修复核心步骤】
            % 获取当前 App (MW_V1.mlapp) 所在的文件夹路径
            currentAppPath = fileparts(mfilename('fullpath')); 
            
            % 拼接出存放画图代码的子文件夹路径: ...\Code_V1\Smith_Plot
            smithScriptPath = fullfile(currentAppPath, 'Smith_Plot');
            
            % 将该文件夹加入 MATLAB 搜索路径
            addpath(smithScriptPath);
            % -------------------------------------------------------------
        
            % 2. 检查是否安装了 RF Toolbox (Smith圆图依赖此工具箱)
            if isempty(which('smithplot'))
                uialert(app.UIFigure, '未检测到 RF Toolbox，无法绘制 Smith 圆图。', '工具箱缺失');
                return;
            end
            % 3. 准备通用变量结构体
            % (我们将把所有参数打包进 params 传递给子函数)
            params = struct();

            % 3. 初始化通用变量
            f = 0; L = 0; C1 = 0; C2 = 0; 
            Z_Real = 0; Z_Im = 0;
        
            % 4. 根据当前选中的 Tab 进行分支处理
            switch app.TabGroup.SelectedTab 
                
                % =========================================================
                % CASE 1: L型 (右) - 源端并联
                % =========================================================
                case app.Tab_LRight_Home
                    % 1.1 获取该页面特定的频率
                    f = app.EditField_Operat_f.Value; 
                    
                    % 1.2 获取 L, C1, C2 (C3置0)
                    L_uH = app.EditField_LRight_Set_L_2.Value;
                    C1_pF = app.EditField_LRight_Cal_C1.Value;
                    C2_pF = app.EditField_LRight_Cal_C2.Value;
                    
                    % 1.3 获取负载实部和虚部
                    Z_Real = app.EditField_LRight_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_LRight_Target_Z_Im.Value;
        
                    % --- 数据防空检查 ---
                    if C1_pF == 0 && C2_pF == 0
                        uialert(app.UIFigure, '元件参数尚未计算(为0)，请先点击“反向计算所需电容值”！', '数据不完整');
                        return;
                    end
                    
                    % --- 准备参数结构体传递给子程序 ---
                    % 将单位统一转换为标准单位 (Hz, H, F, Ohm)
                    params.f = f * 1e6;
                    params.L = L_uH * 1e-6;
                    params.C1 = C1_pF * 1e-12;
                    params.C2 = C2_pF * 1e-12;
                    params.ZL = Z_Real + 1j * Z_Im;
                    params.Z0 = 50; % 系统阻抗
                    
                    % --- 调用 L型(右) 的 Smith 动画子程序 ---
                    try
                        % 因为前面已经 addpath 了，这里可以直接调用文件名
                        SmithAnimator_LRight(params);
                    catch ME
                        uialert(app.UIFigure, ['绘图出错: ' ME.message], '错误');
                    end
        
                % =========================================================
                % CASE 2: L型 (左) - 负载端并联
                % =========================================================
                case app.Tab_LLeft_Home
                    % 1. 获取 L-Left 页面特定的数据 (注意控件名称后缀 _LLeft)
                    f = app.EditField_Operat_f_LLeft.Value; 
                    
                    % 注意：使用反向计算区域的 L, C1, C2
                    L_uH = app.EditField_LLeft_Set_L_2.Value;
                    C1_pF = app.EditField_LLeft_Cal_C1.Value;
                    C2_pF = app.EditField_LLeft_Cal_C2.Value;
                    
                    % 获取负载
                    Z_Real = app.EditField_LLeft_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_LLeft_Target_Z_Im.Value;
                    
                    % 2. 防空检查
                    if C1_pF == 0 && C2_pF == 0
                        uialert(app.UIFigure, '请先点击“反向计算”获取电容值！', '数据不完整');
                        return;
                    end
                    
                    % 3. 填充结构体 (单位换算)
                    params.f = f * 1e6;
                    params.L = L_uH * 1e-6;
                    params.C1 = C1_pF * 1e-12;
                    params.C2 = C2_pF * 1e-12;
                    params.ZL = Z_Real + 1j * Z_Im;
                    params.Z0 = 50;
                    
                    % 4. 调用 L-Left 动画 (我们需要新建这个文件)
                    try
                        SmithAnimator_LLeft(params); % <--- 这里调用新函数
                    catch ME
                        uialert(app.UIFigure, ['绘图出错: ' ME.message], '错误');
                    end
                     
                % =========================================================
                % CASE 3: T型电路 - 三元件匹配
                % =========================================================
                case app.Tab_T_Home
                    % 1. 获取 T-Network 数据 (使用反向计算区域的结果)
                    f = app.EditField_Operat_f_T.Value; 
                    L_uH = app.EditField_T_Set_L_2.Value;
                    C1_pF = app.EditField_T_Cal_C1.Value;
                    C2_pF = app.EditField_T_Cal_C2.Value;
                    C3_pF = app.EditField_T_Set_C3.Value; % 选定电容 C3
                    
                    Z_Real = app.EditField_T_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_T_Target_Z_Im.Value;
        
                    % 2. 防空检查
                    if C1_pF == 0 || C2_pF == 0
                        uialert(app.UIFigure, '请先点击“反向计算”获取 C1 和 C2 的计算值！', '数据不完整');
                        return;
                    end
                    
                    % 3. 填充结构体 (单位换算为标准单位)
                    params.f = f * 1e6;
                    params.L = L_uH * 1e-6;
                    params.C1 = C1_pF * 1e-12;
                    params.C2 = C2_pF * 1e-12;
                    params.C3 = C3_pF * 1e-12;
                    params.ZL = Z_Real + 1j * Z_Im;
                    params.Z0 = 50;
                    
                    % 4. 调用 T 型动画子程序
                    try
                        SmithAnimator_T(params);
                    catch ME
                        uialert(app.UIFigure, ['绘图出错: ' ME.message], '错误');
                    end
                     
                % =========================================================
                % CASE 4: PiⅠ型 (C-LC-C) - 混合匹配
                % =========================================================
                case app.Tab_pi1_Home
                    % 1. 获取 Pi1 页面数据
                    f = app.EditField_Operat_f_pi1.Value; 
                    
                    % 2. 获取元件值 
                    % 注意：使用反向计算区域的值
                    L_uH  = app.EditField_pi1_Set_L_2.Value;   % 选定的 L
                    C3_pF = app.EditField_pi1_Set_C3_2.Value;  % 选定的 C3
                    C1_pF = app.EditField_pi1_Cal_C1.Value;    % 计算出的 C1
                    C2_pF = app.EditField_pi1_Cal_C2.Value;    % 计算出的 C2
                    
                    % 3. 获取目标负载
                    Z_Real = app.EditField_pi1_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_pi1_Target_Z_Im.Value;
        
                    % 4. 防空检查
                    if C1_pF == 0 || C2_pF == 0
                        uialert(app.UIFigure, '请先点击“反向计算”获取 C1 和 C2 的计算值！', '数据不完整');
                        return;
                    end
                    
                    % 5. 填充结构体 (单位换算为标准单位: Hz, H, F, Ohm)
                    params.f  = f * 1e6;
                    params.L  = L_uH * 1e-6;
                    params.C1 = C1_pF * 1e-12;
                    params.C2 = C2_pF * 1e-12;
                    params.C3 = C3_pF * 1e-12;
                    params.ZL = Z_Real + 1j * Z_Im;
                    params.Z0 = 50;
                    
                    % 6. 调用 Pi1 型动画子程序
                    try
                        SmithAnimator_pi1(params);
                    catch ME
                        uialert(app.UIFigure, ['绘图出错: ' ME.message], '错误');
                    end
                     
                % =========================================================
                % CASE 5: PiⅡ型 (源端调节型) - 混合匹配
                % =========================================================
                case app.Tab_pi2_Home
                    % 1. 获取 Pi2 页面数据
                    f = app.EditField_Operat_f_pi2.Value; 
                    
                    % 2. 获取元件值 
                    % 注意：在 Pi2 反向计算中，L 和 C3 是“已知/设置值”，C1 和 C2 是“计算值”
                    L_uH  = app.EditField_pi2_Set_L_2.Value;   % 选定的 L
                    C3_pF = app.EditField_pi2_Set_C3.Value;    % 选定的 C3 (负载端固定)
                    C1_pF = app.EditField_pi2_Cal_C1.Value;    % 计算出的 C1 (源端)
                    C2_pF = app.EditField_pi2_Cal_C2.Value;    % 计算出的 C2 (中间)
                    
                    % 3. 获取目标负载
                    Z_Real = app.EditField_pi2_Target_Z_Real.Value; 
                    Z_Im   = app.EditField_pi2_Target_Z_Im.Value;
        
                    % 4. 防空检查
                    if C1_pF == 0 || C2_pF == 0
                        uialert(app.UIFigure, '请先点击“反向计算”获取 C1 和 C2 的计算值！', '数据不完整');
                        return;
                    end
                    
                    % 5. 填充结构体 (单位换算为标准单位: Hz, H, F, Ohm)
                    params.f  = f * 1e6;
                    params.L  = L_uH * 1e-6;
                    params.C1 = C1_pF * 1e-12;
                    params.C2 = C2_pF * 1e-12;
                    params.C3 = C3_pF * 1e-12;
                    params.ZL = Z_Real + 1j * Z_Im;
                    params.Z0 = 50;
                    
                    % 6. 调用 Pi2 型动画子程序
                    try
                        SmithAnimator_pi2(params);
                    catch ME
                        uialert(app.UIFigure, ['绘图出错: ' ME.message], '错误');
                    end
                     
                otherwise
                    % 默认处理
            end
        end

        % Button pushed function: Button_Readme_L_Left
        function Button_Readme_L_LeftPushed(app, event)
            % ---------------------------------------------------------
            % 1. 【路径修复】确保 MATLAB 能找到子文件夹里的文件
            % 获取当前主程序(MW_V1)所在的文件夹路径
            currentPath = fileparts(mfilename('fullpath')); 
            % 拼接出说明书所在的子文件夹路径
            readmePath = fullfile(currentPath, 'Readme');
            % 将该路径加入 MATLAB 搜索路径 (否则会报错找不到文件)
            addpath(readmePath);
            % ---------------------------------------------------------
            % 2. 检查窗口是否已经存在且有效
            % 注意：这里把 app.ReadmeApp 改成了您的 app.ReadmeApp_L_Left
            if isempty(app.ReadmeApp_L_Left) || ~isvalid(app.ReadmeApp_L_Left)
                
                % 3. 创建新窗口并赋值给属性“抓住”它
                app.ReadmeApp_L_Left = Readme_L_Left;
                
            else
                % 4. 如果已经存在，直接带到最前面
                figure(app.ReadmeApp_L_Left.UIFigure);
            end
        end

        % Button pushed function: Button_LLeft_Forward
        function Button_LLeft_ForwardPushed(app, event)
            % 1. 获取输入参数 (注意控件名称改为 LLeft)
            f_MHz = app.EditField_Operat_f_LLeft.Value; % 频率
            L_uH = app.EditField_LLeft_Set_L_1.Value;   % 电感
            
            % 获取电容扫描范围
            C1_min_pF = app.EditField_LLeft_Set_C1_min.Value;
            C1_max_pF = app.EditField_LLeft_Set_C1_max.Value;
            C2_min_pF = app.EditField_LLeft_Set_C2_min.Value;
            C2_max_pF = app.EditField_LLeft_Set_C2_max.Value;
            
            % 2. 单位换算
            w = 2 * pi * f_MHz * 1e6;
            L = L_uH * 1e-6;
            min_cap_limit = 0.01; 
            
            C1_min = max(min(C1_min_pF, C1_max_pF), min_cap_limit) * 1e-12;
            C1_max = max(max(C1_min_pF, C1_max_pF), min_cap_limit) * 1e-12;
            C2_min = max(min(C2_min_pF, C2_max_pF), min_cap_limit) * 1e-12;
            C2_max = max(max(C2_min_pF, C2_max_pF), min_cap_limit) * 1e-12;
            
            % 3. 网格扫描
            steps = 50; 
            c1_vec = linspace(C1_min, C1_max, steps);
            c2_vec = linspace(C2_min, C2_max, steps);
            [C1_grid, C2_grid] = meshgrid(c1_vec, c2_vec);
            
            % 4. 【核心修改】L-Left 拓扑阻抗推导
            % 视角：从负载端向源端看，求共轭匹配阻抗。
            % 路径：源(50) -> 串联(L+C2) -> 并联(C1) -> 负载接口
            
            % Step A: 源端(50Ω) 串联 L 和 C2
            % Z_series_branch = j*w*L + 1/(j*w*C2) = j(wL - 1/wC2)
            Z_series = 50 + 1j .* (w .* L - 1 ./ (w .* C2_grid));
            
            % Step B: 转换为导纳以便并联 C1
            Y_series = 1 ./ Z_series;
            
            % Step C: 并联 C1 (电纳为 jwC1)
            Y_total_seen = Y_series + 1j .* w .* C1_grid;
            
            % Step D: 转换回阻抗
            Z_total_seen = 1 ./ Y_total_seen;
            
            % Step E: 负载必须是上述阻抗的“共轭”才能匹配
            Z_Load_Matrix = conj(Z_total_seen);
            
            % 5. 提取极值并显示 (与之前逻辑相同)
            R_vals = real(Z_Load_Matrix);
            X_vals = imag(Z_Load_Matrix);
            
            % 过滤掉可能的非物理值 (如负电阻，虽然理论上不会出现)
            R_vals(R_vals < 0) = NaN;
            
            app.EditField_LLeft_Cal_Zmin_Real.Value = min(R_vals(:));
            app.EditField_LLeft_Cal_Zmax_Real.Value = max(R_vals(:));
            app.EditField_LLeft_Cal_Zmin_Im.Value = min(X_vals(:));
            app.EditField_LLeft_Cal_Zmax_Im.Value = max(X_vals(:));
        end

        % Button pushed function: Button_LLeft_Backward
        function Button_LLeft_BackwardPushed(app, event)
            % 1. 获取输入参数
            f_MHz = app.EditField_Operat_f_LLeft.Value;  % 注意频率控件可能不同
            L_uH = app.EditField_LLeft_Set_L_2.Value;    % 左侧反向计算的电感
            
            % 获取目标负载 (注意控件名称)
            R_L = app.EditField_LLeft_Target_Z_Real.Value; 
            X_L = app.EditField_LLeft_Target_Z_Im.Value;   
            
            % 2. 【核心修改】参数检查：L-Left 要求 R_L > 50
            if R_L <= 50
                uialert(app.UIFigure, ['L型(左)电路要求负载实部必须大于 50 欧姆！', newline, ...
                    '当前 R_L = ', num2str(R_L), 'Ω。', newline, ...
                    '对于低阻负载，请使用 L型(右) 页面。'], '拓扑选择错误');
                return;
            end
            
            % 3. 单位换算
            w = 2 * pi * f_MHz * 1e6;
            L = L_uH * 1e-6;
            
            % 4. 核心计算算法 (通用导纳法，支持复数负载)
            % ----------------------------------------------------
            % 目标：负载并联C1后，其等效串联电阻变为 50Ω
            
            % 4.1 将负载转换为导纳 Y_L = G_L + jB_L
            Y_L = 1 / (R_L + 1j * X_L);
            G_L = real(Y_L);
            B_L = imag(Y_L);
            
            % 4.2 计算所需的并联电纳 B_total
            % 公式：Real(1 / (G_L + jB_total)) = 50
            % 推导得：G_L / (G_L^2 + B_total^2) = 50
            % B_total^2 = G_L/50 - G_L^2
            
            val_inside_sqrt = G_L/50 - G_L^2;
            
            if val_inside_sqrt < 0
                uialert(app.UIFigure, '无法匹配：负载电导过大，无法变换到50欧姆。', '无解');
                return;
            end
            
            % B_total 有两个解 (+/-)，我们需要选择能通过正电容 C1 实现的那个
            % B_total = B_L + w*C1  =>  w*C1 = B_total - B_L
            % 我们需要 w*C1 > 0
            
            B_target_pos = sqrt(val_inside_sqrt);
            B_target_neg = -sqrt(val_inside_sqrt);
            
            C1_val = -1; % 初始化为无效值
            B_chosen = 0;
            
            % 尝试正根
            C1_opt1 = (B_target_pos - B_L) / w;
            % 尝试负根
            C1_opt2 = (B_target_neg - B_L) / w;
            
            % 优先选正值且较小的电容（工程上更优），或者只要是正值
            if C1_opt1 > 0 && C1_opt2 > 0
                [C1_val, idx] = min([C1_opt1, C1_opt2]);
                if idx == 1, B_chosen = B_target_pos; else, B_chosen = B_target_neg; end
            elseif C1_opt1 > 0
                C1_val = C1_opt1;
                B_chosen = B_target_pos;
            elseif C1_opt2 > 0
                C1_val = C1_opt2;
                B_chosen = B_target_neg;
            else
                uialert(app.UIFigure, '无法匹配：所需的并联电容计算为负值 (负载容性过大或感性过大无法补偿)。', '无解');
                app.EditField_LLeft_Cal_C1.Value = 0;
                app.EditField_LLeft_Cal_C2.Value = 0;
                return;
            end
            
            % 4.3 计算 C2 (串联电容)
            % 此时并联部分的阻抗 Z_par = 1 / (G_L + j*B_chosen)
            Z_par = 1 / (G_L + 1j * B_chosen);
            X_par = imag(Z_par);
            
            % 匹配条件：串联支路电抗 + 并联支路电抗 = 0
            % X_series + X_par = 0  =>  X_series = -X_par
            % X_series = wL - 1/(wC2)
            % -X_par = wL - 1/(wC2)  =>  1/(wC2) = wL + X_par
            
            denom_C2 = w * L + X_par;
            
            if denom_C2 <= 0
                uialert(app.UIFigure, '无法匹配：需要串联负电容 (请尝试减小电感 L 的值)。', '无解');
                app.EditField_LLeft_Cal_C1.Value = 0;
                app.EditField_LLeft_Cal_C2.Value = 0;
                return;
            else
                C2_val = 1 / (w * denom_C2);
            end
            
            % 5. 结果显示 (换算为 pF)
            app.EditField_LLeft_Cal_C1.Value = C1_val * 1e12;
            app.EditField_LLeft_Cal_C2.Value = C2_val * 1e12;
        end

        % Button pushed function: Button_T_Forward
        function Button_T_ForwardPushed(app, event)
            % 1. 获取输入参数
            f_MHz = app.EditField_Operat_f_T.Value;
            L_uH = app.EditField_T_Set_L_1.Value;
            
            % 获取电容扫描范围
            C1_min_pF = app.EditField_T_Set_C1_min.Value;
            C1_max_pF = app.EditField_T_Set_C1_max.Value;
            
            C2_min_pF = app.EditField_T_Set_C2_min.Value;
            C2_max_pF = app.EditField_T_Set_C2_max.Value;
            
            C3_min_pF = app.EditField_T_Set_C3_min.Value;
            C3_max_pF = app.EditField_T_Set_C3_max.Value;
            
            % 2. 单位换算与防错处理
            w = 2 * pi * f_MHz * 1e6;
            L = L_uH * 1e-6;
            min_cap = 0.01; % 防止除以0
            
            % 转换并确保非零
            C1_min = max(min(C1_min_pF, C1_max_pF), min_cap) * 1e-12;
            C1_max = max(max(C1_min_pF, C1_max_pF), min_cap) * 1e-12;
            
            C2_min = max(min(C2_min_pF, C2_max_pF), min_cap) * 1e-12;
            C2_max = max(max(C2_min_pF, C2_max_pF), min_cap) * 1e-12;
            
            C3_min = max(min(C3_min_pF, C3_max_pF), min_cap) * 1e-12;
            C3_max = max(max(C3_min_pF, C3_max_pF), min_cap) * 1e-12;
            
            % 3. 生成网格 (3D扫描)
            % 为了计算速度，每个维度取 20-30 个点
            steps = 25; 
            c1_vec = linspace(C1_min, C1_max, steps);
            c2_vec = linspace(C2_min, C2_max, steps);
            c3_vec = linspace(C3_min, C3_max, steps);
            
            [C1_g, C2_g, C3_g] = meshgrid(c1_vec, c2_vec, c3_vec);
            
            % 4. 核心阻抗计算
            % 逻辑：计算网络输出阻抗 Z_out (源端接50欧，从负载端看进去的阻抗)
            % 匹配条件：Load = Conj(Z_out)
            
            % 4.1 左侧支路阻抗 (源阻抗 50 + 串联 C3)
            Z_left_branch = 50 + 1 ./ (1j * w .* C3_g);
            
            % 4.2 中间并联支路阻抗 (L + C2)
            Z_shunt_branch = 1j * w * L + 1 ./ (1j * w .* C2_g);
            
            % 4.3 计算节点处的等效阻抗 (Z_left_branch 与 Z_shunt_branch 并联)
            % Z_parallel = (Z1 * Z2) / (Z1 + Z2)
            Z_node = (Z_left_branch .* Z_shunt_branch) ./ (Z_left_branch + Z_shunt_branch);
            
            % 4.4 加上右侧串联电容 C1 得到总输出阻抗
            Z_out = Z_node + 1 ./ (1j * w .* C1_g);
            
            % 4.5 负载必须是 Z_out 的共轭
            Z_Load_Matrix = conj(Z_out);
            
            % 5. 提取结果并显示
            R_vals = real(Z_Load_Matrix);
            X_vals = imag(Z_Load_Matrix);
            
            % 过滤无效值 (实部必须大于0)
            valid_mask = R_vals > 0;
            if any(valid_mask(:))
                R_vals = R_vals(valid_mask);
                X_vals = X_vals(valid_mask);
                
                app.EditField_T_Cal_Zmin_Real.Value = min(R_vals);
                app.EditField_T_Cal_Zmax_Real.Value = max(R_vals);
                app.EditField_T_Cal_Zmin_Im.Value = min(X_vals);
                app.EditField_T_Cal_Zmax_Im.Value = max(X_vals);
            else
                app.EditField_T_Cal_Zmin_Real.Value = 0;
                app.EditField_T_Cal_Zmax_Real.Value = 0;
            end
        end

        % Button pushed function: Button_T_Backward
        function Button_T_BackwardPushed(app, event)
            % 1. 获取界面输入参数
            % -----------------------------------------------------------
            f_MHz = app.EditField_Operat_f_T.Value; % 频率
            
            % 用户选定的固定值 (根据界面截图)
            L_uH = app.EditField_T_Set_L_2.Value;   % 选定电感 L
            C3_pF = app.EditField_T_Set_C3.Value; % 选定电容 C3            
            % 目标负载
            R_L = app.EditField_T_Target_Z_Real.Value;
            X_L = app.EditField_T_Target_Z_Im.Value;
            
            % 2. 基础参数检查与防错
            % -----------------------------------------------------------
            if C3_pF <= 0
                uialert(app.UIFigure, '必须设定一个有效的 C3 值(>0)才能确定中间虚拟阻抗。', '参数错误');
                return;
            end
            if R_L <= 0
                uialert(app.UIFigure, '负载实部必须大于 0。', '参数错误');
                return;
            end
        
            % 3. 单位换算
            % -----------------------------------------------------------
            w = 2 * pi * f_MHz * 1e6;
            L = L_uH * 1e-6;
            C3 = C3_pF * 1e-12;
            
            % 4. 核心算法：虚拟电阻匹配法
            % 拓扑：Source(50) -- C3 -- [Node] -- C1 -- Load
            %                      |
            %                   (L+C2)
            %                      |
            %                     GND
            
            % Step A: 计算左侧（源端）转换后的导纳和虚拟电阻
            % 源端阻抗 Z_S = 50 + 0j
            % 左侧支路总阻抗 Z_left_branch = 50 - j/(w*C3)
            Z_left = 50 - 1j / (w * C3);
            
            % 转换为导纳 Y_left = G_node + j*B_node_left
            Y_left = 1 / Z_left;
            G_node = real(Y_left);        % 中间节点的电导
            B_node_left = imag(Y_left);   % 左侧贡献的电纳
            
            % 计算虚拟电阻 R_virtual = 1/G_node
            % 这是整个匹配过程的核心“中间跳板”
            R_virtual = 1 / G_node;
            
            % Step B: 检查可行性
            % 负载端通过串联 C1 变换后，其并联电阻必须能达到 R_virtual
            % 物理限制：串联电抗只能将电阻“向上”变换。
            % 因此，只有当 R_virtual >= R_L 时才有解。
            if R_virtual < R_L
                uialert(app.UIFigure, sprintf(['无法匹配！\n', ...
                    '当前选定的 C3 (%.2f pF) 产生的中间虚拟电阻 (%.1f Ω) 小于负载电阻 (%.1f Ω)。\n', ...
                    '建议：减小 C3 的值以提高中间虚拟电阻。'], C3_pF, R_virtual, R_L), '无解');
                app.EditField_T_Cal_C1.Value = 0;
                app.EditField_T_Cal_C2.Value = 0;
                return;
            end
            
            % Step C: 计算 C1
            % 我们需要将负载 (RL + jXL) 串联 C1 后，其对应的并联电导等于 G_node
            % 设串联支路总电抗 X_branch_right = X_L - 1/(w*C1)
            % 并联电导公式：Gp = RL / (RL^2 + X_branch_right^2)
            % 令 Gp = G_node，解得: X_branch_right^2 = RL/G_node - RL^2
            
            temp_val = R_L / G_node - R_L^2; 
            % 理论上 temp_val >= 0，因为前面已经检查了 R_virtual >= R_L
            
            X_branch_mag = sqrt(temp_val);
            
            % 这里有两个数学解：X_branch = +mag 或 -mag
            % 物理含义：负载支路呈现感性(+mag)或容性(-mag)
            % X_branch = X_L - 1/(w*C1)  =>  1/(w*C1) = X_L - X_branch
            
            % 计算两个可能的 C1 值
            % 方案1: X_branch 取正 (感性)
            val_inv_C1_1 = w * (X_L - X_branch_mag);
            % 方案2: X_branch 取负 (容性)
            val_inv_C1_2 = w * (X_L + X_branch_mag);
            
            C1_opt1 = -1; 
            C1_opt2 = -1;
            
            if val_inv_C1_1 > 0, C1_opt1 = 1 / val_inv_C1_1; end
            if val_inv_C1_2 > 0, C1_opt2 = 1 / val_inv_C1_2; end
            
            % 策略：选择正值。如果两个都为正，通常选择电容值较小（容抗较大）的那个，
            % 或者选择使得中间节点Q值较低的那个以获得更宽带宽。
            % 这里简单逻辑：优先选正值，且存在的那个。
            if C1_opt1 > 0
                C1 = C1_opt1;
                X_branch_right_chosen = X_branch_mag;
            elseif C1_opt2 > 0
                C1 = C1_opt2;
                X_branch_right_chosen = -X_branch_mag;
            else
                uialert(app.UIFigure, '无法匹配：计算出的 C1 为负值 (负载感性过大无法补偿)。', '无解');
                app.EditField_T_Cal_C1.Value = 0;
                app.EditField_T_Cal_C2.Value = 0;
                return;
            end
            
            % Step D: 计算 C2
            % 此时，右侧支路（负载+C1）转换到中间节点的电纳：
            % Y_right = 1 / (RL + j * X_branch_right_chosen)
            % 我们已经保证了 Real(Y_right) == G_node
            B_node_right = imag(1 / (R_L + 1j * X_branch_right_chosen));
            
            % 谐振条件：中间节点总电纳为 0
            % B_total = B_node_left + B_node_right + B_shunt = 0
            % 所以中间并联支路 (L+C2) 必须提供的电纳为：
            B_shunt_needed = -(B_node_left + B_node_right);
            
            % 并联支路阻抗 Z_shunt = j*w*L + 1/(j*w*C2) = j(w*L - 1/(w*C2))
            % 并联支路电纳 Y_shunt = 1/Z_shunt = -j / (w*L - 1/(w*C2))
            % B_shunt = -1 / (w*L - 1/(w*C2))
            
            % 求解 C2:
            % w*L - 1/(w*C2) = -1 / B_shunt_needed
            % 1/(w*C2) = w*L + 1/B_shunt_needed
            
            if abs(B_shunt_needed) < 1e-9
                % 极少数情况：刚好不需要并联支路（纯电阻匹配），或者是开路
                % 在这里处理为无解或极大值
                uialert(app.UIFigure, '无需并联电抗补偿，C2 无解。', '特殊情况');
                return;
            end
            % 计算 1/(w*C2) 的理论值
            val_inv_wC2 = w * L + 1 / B_shunt_needed;
            
            % 【核心逻辑判断】：如果电感感抗 wL 过大，会使得 val_inv_wC2 变为负数
            if val_inv_wC2 <= 0
                uialert(app.UIFigure, ['无法匹配：C2 计算结果为负。请尝试调整 L 或 C3 的值。', '无解', newline, ...
                    '物理原因：电感的感抗已超过匹配所需的总负电纳需求。'], '计算受限');
                app.EditField_T_Cal_C1.Value = C1 * 1e12; % C1 还是可以显示的，作为一个参考
                app.EditField_T_Cal_C2.Value = 0;
                return;
            end
            
            C2 = 1 / (w * val_inv_wC2);
            
            % 5. 结果显示 (换算为 pF)
            % -----------------------------------------------------------
            app.EditField_T_Cal_C1.Value = C1 * 1e12;
            app.EditField_T_Cal_C2.Value = C2 * 1e12;
        end

        % Button pushed function: Button_Readme_T
        function Button_Readme_TPushed(app, event)
            % 1. 路径修复
            currentPath = fileparts(mfilename('fullpath')); 
            readmePath = fullfile(currentPath, 'Readme'); % 确保 Readme_T.mlapp 在这个文件夹里
            addpath(readmePath);
            
            % 2. 检查窗口
            if isempty(app.ReadmeApp_T) || ~isvalid(app.ReadmeApp_T)
                try
                    app.ReadmeApp_T = Readme_T; % 创建 T型说明书窗口
                catch ME
                    uialert(app.UIFigure, ['无法打开说明书: ' ME.message], '错误');
                end
            else
                figure(app.ReadmeApp_T.UIFigure); % 带到前台
            end
        end

        % Button pushed function: Button_pi1_Forward
        function Button_pi1_ForwardPushed(app, event)
            % =====================================================================
            % 正向计算 (修正版)：网格扫描法
            % 解决问题：之前只扫描极值点，无法覆盖非线性阻抗变换的真实边界。
            % 现在使用 linspace 对 C1, C2, C3 进行 10~15 步的细分扫描。
            % =====================================================================
            
            % 1. 读取基础参数
            f = app.EditField_Operat_f_pi1.Value * 1e6; % MHz -> Hz
            w = 2 * pi * f;
            Z0 = 50;
            
            % 2. 读取左侧元件参数
            L = app.EditField_pi1_Set_L.Value * 1e-6; % uH -> H
            
            % 读取并检查电容范围 (pF -> F)
            % 如果 Min 和 Max 相等，linspace 会自动处理为单点
            C1_min = app.EditField_pi1_Set_C1_min.Value * 1e-12;
            C1_max = app.EditField_pi1_Set_C1_max.Value * 1e-12;
            
            C2_min = app.EditField_pi1_Set_C2_min.Value * 1e-12;
            C2_max = app.EditField_pi1_Set_C2_max.Value * 1e-12;
            
            C3_min = app.EditField_pi1_Set_C3_min.Value * 1e-12;
            C3_max = app.EditField_pi1_Set_C3_max.Value * 1e-12;
            
            % 3. 定义扫描精度 (点数越多越准，建议 10-20)
            steps = 50;
            
            % 生成扫描向量
            C1_vec = linspace(C1_min, C1_max, steps);
            C2_vec = linspace(C2_min, C2_max, steps);
            C3_vec = linspace(C3_min, C3_max, steps);
            
            % 4. 预分配结果数组 (提高速度)
            total_points = length(C1_vec) * length(C2_vec) * length(C3_vec);
            Z_results = zeros(1, total_points);
            idx = 1;
            
            % 5. 嵌套循环扫描 (Grid Search)
            for c3 = C3_vec
                % Step 1: 源端并联 C3 (这一步只与 C3 有关，放在外层减少计算)
                Y_S = 1/Z0 + 1j*w*c3;
                Z_S_eff = 1/Y_S;
                
                for c2 = C2_vec
                    % Step 2: 串联臂 L + C2
                    % 注意防止 C2=0 (虽然界面限制了，但防错更好)
                    if c2 < 1e-15, continue; end 
                    
                    Z_branch = 1j*w*L + 1/(1j*w*c2);
                    Z_before_C1 = Z_S_eff + Z_branch;
                    Y_before_C1 = 1/Z_before_C1;
                    
                    for c1 = C1_vec
                        % Step 3: 负载端并联 C1
                        % 从负载看进去的输入导纳 Y_in
                        Y_in = Y_before_C1 + 1j*w*c1;
                        Z_in = 1/Y_in;
                        
                        % Step 4: 匹配条件 (共轭)
                        Z_load_conjugate = conj(Z_in);
                        
                        % 存储结果
                        Z_results(idx) = Z_load_conjugate;
                        idx = idx + 1;
                    end
                end
            end
            
            % 剔除未填充的零 (如果有跳过的情况)
            Z_results = Z_results(1:idx-1);
            
            % 6. 提取并显示结果
            if isempty(Z_results)
                return; 
            end
            
            % 实部范围
            R_vals = real(Z_results);
            % 为了防止数值噪声导致显示极小的负数（如 -1e-15），取 max(0, ...)
            app.EditField_pi1_Cal_Zmin_Real.Value = max(0, min(R_vals));
            app.EditField_pi1_Cal_Zmax_Real.Value = max(R_vals);
            
            % 虚部范围
            X_vals = imag(Z_results);
            app.EditField_pi1_Cal_Zmin_Im.Value = min(X_vals);
            app.EditField_pi1_Cal_Zmax_Im.Value = max(X_vals);
            
            % (可选) 可以在这里打印一下调试信息
            % fprintf('Calculated %d points. Max R: %.2f\n', length(Z_results), max(R_vals));
        end

        % Button pushed function: Button_pi1_Backward
        function Button_pi1_BackwardPushed(app, event)
            % =====================================================================
            % 反向计算：已知 Z_Load, L, C3，求解匹配所需的 C1 和 C2
            % 算法思路：阻抗平衡法
            % 1. 将源端(50Ω || C3)变换为等效串联阻抗 Z_S_eff
            % 2. 调节负载端并联 C1，使得 Real(Z_Load || C1) == Real(Z_S_eff)
            % 3. 调节中间串联 C2，抵消两端的剩余虚部
            % =====================================================================
            
            % 1. 读取参数
            f = app.EditField_Operat_f_pi1.Value * 1e6;
            w = 2 * pi * f;
            Z0 = 50;
            
            % 注意：反向计算区域的 L 和 C3 控件名称带有 _2 后缀
            L = app.EditField_pi1_Set_L_2.Value * 1e-6; 
            C3 = app.EditField_pi1_Set_C3_2.Value * 1e-12; 
            
            % 目标负载
            R_L = app.EditField_pi1_Target_Z_Real.Value;
            X_L = app.EditField_pi1_Target_Z_Im.Value;
            Z_target = R_L + 1j*X_L;
            Y_target = 1/Z_target;
            G_L = real(Y_target);
            B_L = imag(Y_target);
            
            % --- 步骤 1: 源端状态 (50 || C3) ---
            Y_S = 1/Z0 + 1j*w*C3;
            Z_S_eff = 1/Y_S; 
            R_S_eff = real(Z_S_eff); % 源端等效串联电阻
            X_S_eff = imag(Z_S_eff); % 源端等效串联电抗
            
            % --- 步骤 2: 求解 C1 (电阻匹配) ---
            % 目标：Real( 1 / (G_L + j(B_L + wC1)) ) == R_S_eff
            % 推导得到一元二次方程或直接解：
            % G_L / (G_L^2 + (B_L + wC1)^2) = R_S_eff
            % (B_L + wC1)^2 = G_L/R_S_eff - G_L^2
            
            delta = G_L / R_S_eff - G_L^2;
            
            if delta < 0
                uialert(app.UIFigure, ...
                    '无解：当前选定的 C3 导致源端等效电阻过大，无法匹配该负载。请减小 C3 或更改拓扑。', ...
                    '计算失败');
                return;
            end
            
            % 求解 C1 (通常有两个解，取正实数)
            term = sqrt(delta);
            % 解1: B_L + wC1 = term
            C1_a = (term - B_L) / w;
            % 解2: B_L + wC1 = -term
            C1_b = (-term - B_L) / w;
            
            % 优选正值且较小的 C1 (工程习惯)
            C1_candidates = [C1_a, C1_b];
            C1_valid = C1_candidates(C1_candidates > 0);
            
            if isempty(C1_valid)
                uialert(app.UIFigure, '无解：计算得到的 C1 为负值。', '计算失败');
                return;
            end
            
            C1_sol = min(C1_valid); % 选最小的正电容
            
            % --- 步骤 3: 求解 C2 (电抗匹配) ---
            % 计算负载端并联 C1 后的等效阻抗
            Y_L_new = G_L + 1j*(B_L + w*C1_sol);
            Z_L_new = 1/Y_L_new;
            X_L_new = imag(Z_L_new);
            
            % 中间串联臂 (L+C2) 需要提供的电抗 X_branch
            % 总回路方程：Z_S_eff + Z_branch + Z_L_new = 0 (共轭匹配观点)
            % 或者：Im(Z_S_eff) + X_branch + Im(Z_L_new) = 0
            X_branch_needed = -(X_S_eff + X_L_new);
            
            % X_branch = wL - 1/(wC2)
            % 1/(wC2) = wL - X_branch_needed
            denom = w*L - X_branch_needed;
            
            if denom <= 0
                uialert(app.UIFigure, ...
                    sprintf('无解：所需串联电容 C2 不存在 (需要 %s 电感)。\n当前 L 太小，无法提供足够的正电抗，或 L 太大无法被 C2 抵消。', ...
                    string(denom)), '计算失败');
                return;
            end
            
            C2_sol = 1 / (w * denom);
            
            % --- 4. 结果显示 ---
            app.EditField_pi1_Cal_C1.Value = C1_sol * 1e12; % F -> pF
            app.EditField_pi1_Cal_C2.Value = C2_sol * 1e12; % F -> pF
            
            % 成功提示 (可选，去掉注释可开启)
            % uialert(app.UIFigure, '计算成功！', '完成');
        end

        % Button pushed function: Button_Readme_pi1
        function Button_Readme_pi1Pushed(app, event)
            % 1. 路径修复：确保程序能找到 Readme 文件夹
            currentPath = fileparts(mfilename('fullpath')); 
            readmePath = fullfile(currentPath, 'Readme'); 
            addpath(readmePath);
            
            % 2. 检查并打开窗口
            % 检查 app.ReadmeApp_pi1 是否存在且有效 (需要在属性中定义该属性，见下文提示)
            if isempty(app.ReadmeApp_pi1) || ~isvalid(app.ReadmeApp_pi1)
                try
                    % 实例化 Pi1 型说明书窗口 (假设文件名为 Readme_pi1.mlapp)
                    app.ReadmeApp_pi1 = Readme_pi1; 
                catch ME
                    uialert(app.UIFigure, ['无法打开说明书: ' ME.message], '错误');
                end
            else
                % 如果已经打开，将其置顶
                figure(app.ReadmeApp_pi1.UIFigure); 
            end
        end

        % Button pushed function: Button_Readme_pi2
        function Button_Readme_pi2Pushed(app, event)
            % 1. 路径处理：定位 Readme 文件夹
            currentPath = fileparts(mfilename('fullpath')); 
            readmePath = fullfile(currentPath, 'Readme'); 
            addpath(readmePath);
            
            % 2. 窗口管理：创建或置顶 Readme_pi2 窗口
            % 注意：需在 App 属性中预先定义 app.ReadmeApp_pi2
            if isempty(app.ReadmeApp_pi2) || ~isvalid(app.ReadmeApp_pi2)
                try
                    app.ReadmeApp_pi2 = Readme_pi2; % 实例化 Pi2 说明书
                catch ME
                    uialert(app.UIFigure, ['无法打开说明书: ' ME.message], '错误');
                end
            else
                figure(app.ReadmeApp_pi2.UIFigure); % 带到前台
            end
        end

        % Button pushed function: Button_pi2_Forward
        function Button_pi2_ForwardPushed(app, event)
            % =====================================================================
            % 正向计算：Pi (II) 型
            % 拓扑：源(50Ω) || C1 -> 串联(L+C2) -> 并联C3 -> 负载
            % 目标：计算从负载端看进去的共轭阻抗范围 (即最大可匹配负载)
            % 算法：网格扫描法 (Grid Search) 提高覆盖精度
            % =====================================================================
            
            % 1. 读取基础参数
            f = app.EditField_Operat_f_pi2.Value * 1e6; % MHz -> Hz
            w = 2 * pi * f;
            Z0 = 50;
            
            % 2. 读取左侧元件参数 (Forward区域)
            L = app.EditField_pi2_Set_L.Value * 1e-6; % uH -> H
            
            % 读取电容范围 (pF -> F)
            % C1 (源端)
            C1_min = app.EditField_pi2_Set_C1_min.Value * 1e-12;
            C1_max = app.EditField_pi2_Set_C1_max.Value * 1e-12;
            % C2 (串联)
            C2_min = app.EditField_pi2_Set_C2_min.Value * 1e-12;
            C2_max = app.EditField_pi2_Set_C2_max.Value * 1e-12;
            % C3 (负载端)
            C3_min = app.EditField_pi2_Set_C3_min.Value * 1e-12;
            C3_max = app.EditField_pi2_Set_C3_max.Value * 1e-12;
            
            % 3. 定义扫描精度 (建议 12-15 点)
            steps = 50;
            
            C1_vec = linspace(C1_min, C1_max, steps);
            C2_vec = linspace(C2_min, C2_max, steps);
            C3_vec = linspace(C3_min, C3_max, steps);
            
            % 4. 扫描计算
            % 逻辑：源 -> C1 -> L+C2 -> C3 -> Z_in -> Z_matchable = conj(Z_in)
            
            total_points = length(C1_vec) * length(C2_vec) * length(C3_vec);
            Z_results = zeros(1, total_points);
            idx = 1;
            
            for c1 = C1_vec
                % Step 1: 源端变换 (50Ω || C1)
                Y_S = 1/Z0 + 1j*w*c1;
                Z_S_eff = 1/Y_S; % 等效串联阻抗
                
                for c2 = C2_vec
                    if c2 < 1e-15, continue; end % 防止除以0
                    
                    % Step 2: 串联臂 (L + C2)
                    Z_series_branch = 1j*w*L + 1/(1j*w*c2);
                    Z_after_series = Z_S_eff + Z_series_branch;
                    Y_after_series = 1/Z_after_series;
                    
                    for c3 = C3_vec
                        % Step 3: 负载端并联 C3
                        % Z_after_series 是从源过来、经过C3之前的阻抗
                        % 现在并联 C3：Y_in = Y_after_series + jwC3
                        Y_in = Y_after_series + 1j*w*c3;
                        Z_in = 1/Y_in;
                        
                        % Step 4: 匹配负载 (共轭)
                        Z_matchable = conj(Z_in);
                        
                        Z_results(idx) = Z_matchable;
                        idx = idx + 1;
                    end
                end
            end
            
            % 5. 处理结果
            Z_results = Z_results(1:idx-1);
            
            if isempty(Z_results), return; end
            
            R_vals = real(Z_results);
            app.EditField_pi2_Cal_Zmin_Real.Value = max(0, min(R_vals));
            app.EditField_pi2_Cal_Zmax_Real.Value = max(R_vals);
            
            X_vals = imag(Z_results);
            app.EditField_pi2_Cal_Zmin_Im.Value = min(X_vals);
            app.EditField_pi2_Cal_Zmax_Im.Value = max(X_vals);
        end

        % Button pushed function: Button_pi2_Backward
        function Button_pi2_BackwardPushed(app, event)
            % =====================================================================
            % 反向计算：Pi (II) 型
            % 拓扑：源(50Ω) || C1 -> 串联(L+C2) -> 并联C3 -> 负载(Z_Load)
            % 已知：Z_Load, L, C3
            % 求解：C1 (源端), C2 (中间)
            % =====================================================================
            
            % 1. 读取基础参数
            f = app.EditField_Operat_f_pi2.Value * 1e6;
            w = 2 * pi * f;
            
            % 2. 读取反向计算区参数
            % 注意控件名称：L使用_2后缀，C3使用Set_C3(根据对象树推断无后缀或查看属性)
            % 这里假设对象树中是 app.EditField_pi2_Set_C3
            L  = app.EditField_pi2_Set_L_2.Value * 1e-6; 
            C3 = app.EditField_pi2_Set_C3.Value * 1e-12; 
            
            % 读取目标负载
            R_L = app.EditField_pi2_Target_Z_Real.Value;
            X_L = app.EditField_pi2_Target_Z_Im.Value;
            
            if R_L <= 0
                uialert(app.UIFigure, '负载实部必须大于0', '参数错误');
                return;
            end
            
            % --- Step 1: 负载端等效变换 (Load || C3) ---
            Z_L = R_L + 1j*X_L;
            Y_L = 1/Z_L;
            Y_L_eff = Y_L + 1j*w*C3; % 并联 C3
            Z_L_eff = 1/Y_L_eff;
            
            R_Leff = real(Z_L_eff);
            X_Leff = imag(Z_L_eff);
            
            % --- Step 2: 求解 C1 (源端电阻匹配) ---
            % 源端结构：50Ω || C1
            % 变换后的等效串联电阻 R_S_eff 必须等于 R_Leff
            % 公式：R_S_eff = 50 / (1 + (w * C1 * 50)^2)
            % 条件：因为 R_S_eff 最大为 50 (当C1=0时)，所以如果 R_Leff > 50，则此拓扑无解
            
            if R_Leff > 50
                uialert(app.UIFigure, ...
                    sprintf('无解：负载并联C3后的等效电阻 (%.1fΩ) 大于 50Ω。\nPi(II)型源端并联电容结构只能进行“向下”阻抗变换 (匹配 <50Ω 的负载)。\n建议：减小 C3 或改用 Pi(I)型。', R_Leff), ...
                    '阻抗失配');
                return;
            end
            
            % 求解 C1:
            % R_Leff = 50 / (1 + Qs^2)  =>  1 + Qs^2 = 50 / R_Leff
            % Qs^2 = 50/R_Leff - 1
            % Qs = w * C1 * 50
            
            val = 50 / R_Leff - 1;
            if val < 0
                % 理论上前面判断了 >50，这里不会小于0，除非数值误差
                val = 0; 
            end
            
            Qs = sqrt(val);
            C1_sol = Qs / (50 * w);
            
            % --- Step 3: 求解 C2 (中间电抗匹配) ---
            % 源端等效电抗 X_S_eff
            % Z_S_eff = 50 / (1 + j*Qs) = 50(1-jQs)/(1+Qs^2)
            % X_S_eff = -50 * Qs / (1 + Qs^2)
            % 或者直接：X_S_eff = - R_S_eff * Qs
            X_S_eff = - R_Leff * Qs;
            
            % 串联支路必须提供电抗 X_series，使得：
            % X_S_eff + X_series + X_Leff = 0  (共轭匹配原理：总回路电抗为0)
            % 也可以理解为：源端变换到中间的 Z + 串联臂 Z = 负载端变换到中间的 Z 的共轭
            % Real 已匹配，Imag: X_S_eff + X_series = -X_Leff
            
            X_req = -X_Leff - X_S_eff;
            
            % X_req = wL - 1/(wC2)
            % 1/(wC2) = wL - X_req
            denom = w*L - X_req;
            
            if denom <= 0
                uialert(app.UIFigure, ...
                    sprintf('无解：需要串联电容 C2 提供极大的正电抗。\n当前 L (%.2f uH) 太小，或负载容性过大。\n建议：增大 L 或 减小 C3。', L*1e6), ...
                    '电感不足');
                return;
            end
            
            C2_sol = 1 / (w * denom);
            
            % 4. 显示结果
            app.EditField_pi2_Cal_C1.Value = C1_sol * 1e12; % F -> pF
            app.EditField_pi2_Cal_C2.Value = C2_sol * 1e12; % F -> pF
        end

        % Changes arrangement of the app based on UIFigure width
        function updateAppLayout(app, event)
            currentFigureWidth = app.UIFigure.Position(3);
            if(currentFigureWidth <= app.onePanelWidth)
                % Change to a 2x1 grid
                app.GridLayout.RowHeight = {681, 681};
                app.GridLayout.ColumnWidth = {'1x'};
                app.RightPanel.Layout.Row = 2;
                app.RightPanel.Layout.Column = 1;
            else
                % Change to a 1x2 grid
                app.GridLayout.RowHeight = {'1x'};
                app.GridLayout.ColumnWidth = {111, '1x'};
                app.RightPanel.Layout.Row = 1;
                app.RightPanel.Layout.Column = 2;
            end
        end
    end

    % Component initialization
    methods (Access = private)

        % Create UIFigure and components
        function createComponents(app)

            % Get the file path for locating images
            pathToMLAPP = fileparts(mfilename('fullpath'));

            % Create UIFigure and hide until all components are created
            app.UIFigure = uifigure('Visible', 'off');
            app.UIFigure.AutoResizeChildren = 'off';
            app.UIFigure.Color = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.UIFigure.Position = [100 100 908 681];
            app.UIFigure.Name = 'MATLAB App';
            app.UIFigure.SizeChangedFcn = createCallbackFcn(app, @updateAppLayout, true);

            % Create GridLayout
            app.GridLayout = uigridlayout(app.UIFigure);
            app.GridLayout.ColumnWidth = {111, '1x'};
            app.GridLayout.RowHeight = {'1x'};
            app.GridLayout.ColumnSpacing = 0;
            app.GridLayout.RowSpacing = 0;
            app.GridLayout.Padding = [0 0 0 0];
            app.GridLayout.Scrollable = 'on';
            app.GridLayout.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LeftPanel
            app.LeftPanel = uipanel(app.GridLayout);
            app.LeftPanel.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LeftPanel.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.LeftPanel.Layout.Row = 1;
            app.LeftPanel.Layout.Column = 1;

            % Create Button_L_Right
            app.Button_L_Right = uibutton(app.LeftPanel, 'push');
            app.Button_L_Right.ButtonPushedFcn = createCallbackFcn(app, @Button_L_RightPushed, true);
            app.Button_L_Right.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_L_Right.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_L_Right.Position = [6 647 100 23];
            app.Button_L_Right.Text = 'L型电路(右)';

            % Create Button_L_Left
            app.Button_L_Left = uibutton(app.LeftPanel, 'push');
            app.Button_L_Left.ButtonPushedFcn = createCallbackFcn(app, @Button_L_LeftPushed, true);
            app.Button_L_Left.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_L_Left.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_L_Left.Position = [6 568 100 23];
            app.Button_L_Left.Text = 'L型电路(左)';

            % Create Button_T
            app.Button_T = uibutton(app.LeftPanel, 'push');
            app.Button_T.ButtonPushedFcn = createCallbackFcn(app, @Button_TPushed, true);
            app.Button_T.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_T.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_T.Position = [6 487 100 23];
            app.Button_T.Text = 'T型电路';

            % Create Button_pi_1
            app.Button_pi_1 = uibutton(app.LeftPanel, 'push');
            app.Button_pi_1.ButtonPushedFcn = createCallbackFcn(app, @Button_pi_1Pushed, true);
            app.Button_pi_1.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_pi_1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_pi_1.Position = [6 403 100 23];
            app.Button_pi_1.Text = 'π 型电路 Ⅰ';

            % Create Button_pi_2
            app.Button_pi_2 = uibutton(app.LeftPanel, 'push');
            app.Button_pi_2.ButtonPushedFcn = createCallbackFcn(app, @Button_pi_2Pushed, true);
            app.Button_pi_2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_pi_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_pi_2.Position = [6 317 100 23];
            app.Button_pi_2.Text = 'π 型电路 Ⅱ';

            % Create Button_Z2Y
            app.Button_Z2Y = uibutton(app.LeftPanel, 'push');
            app.Button_Z2Y.ButtonPushedFcn = createCallbackFcn(app, @Button_Z2YPushed, true);
            app.Button_Z2Y.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Z2Y.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Z2Y.Position = [6 225 100 23];
            app.Button_Z2Y.Text = '阻抗导纳计算';

            % Create Button_About
            app.Button_About = uibutton(app.LeftPanel, 'push');
            app.Button_About.ButtonPushedFcn = createCallbackFcn(app, @Button_AboutPushed, true);
            app.Button_About.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_About.FontName = 'Times New Roman';
            app.Button_About.FontSize = 14;
            app.Button_About.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_About.Position = [6 51 100 25];
            app.Button_About.Text = 'About';

            % Create Button_Quit
            app.Button_Quit = uibutton(app.LeftPanel, 'push');
            app.Button_Quit.ButtonPushedFcn = createCallbackFcn(app, @Button_QuitPushed, true);
            app.Button_Quit.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Quit.FontName = 'Times New Roman';
            app.Button_Quit.FontSize = 14;
            app.Button_Quit.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Quit.Position = [6 9 100 25];
            app.Button_Quit.Text = 'Quit';

            % Create RightPanel
            app.RightPanel = uipanel(app.GridLayout);
            app.RightPanel.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.RightPanel.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.RightPanel.Layout.Row = 1;
            app.RightPanel.Layout.Column = 2;

            % Create TabGroup
            app.TabGroup = uitabgroup(app.RightPanel);
            app.TabGroup.Position = [1 33 792 647];

            % Create Tab_Welcome
            app.Tab_Welcome = uitab(app.TabGroup);
            app.Tab_Welcome.Title = 'Welcome';
            app.Tab_Welcome.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_Welcome.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout_Welcome
            app.GridLayout_Welcome = uigridlayout(app.Tab_Welcome);
            app.GridLayout_Welcome.RowHeight = {'1x', '4x', '1x', '1x', '1x'};
            app.GridLayout_Welcome.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create Image_Welcome
            app.Image_Welcome = uiimage(app.GridLayout_Welcome);
            app.Image_Welcome.Layout.Row = 2;
            app.Image_Welcome.Layout.Column = 1;
            app.Image_Welcome.ImageSource = fullfile(pathToMLAPP, 'Figure', 'Matlab_Figure.png');

            % Create Label_Welcome
            app.Label_Welcome = uilabel(app.GridLayout_Welcome);
            app.Label_Welcome.HorizontalAlignment = 'center';
            app.Label_Welcome.FontName = '楷体';
            app.Label_Welcome.FontSize = 36;
            app.Label_Welcome.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_Welcome.Layout.Row = 3;
            app.Label_Welcome.Layout.Column = [1 2];
            app.Label_Welcome.Text = '欢迎使用微波技术——阻抗匹配设计系统';

            % Create Label_Designer
            app.Label_Designer = uilabel(app.GridLayout_Welcome);
            app.Label_Designer.HorizontalAlignment = 'center';
            app.Label_Designer.FontName = '楷体';
            app.Label_Designer.FontSize = 24;
            app.Label_Designer.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_Designer.Layout.Row = 4;
            app.Label_Designer.Layout.Column = [1 2];
            app.Label_Designer.Text = '设计者：卢瑞林、卢柯吉';

            % Create Label_Member
            app.Label_Member = uilabel(app.GridLayout_Welcome);
            app.Label_Member.HorizontalAlignment = 'center';
            app.Label_Member.FontName = '楷体';
            app.Label_Member.FontSize = 24;
            app.Label_Member.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_Member.Layout.Row = 5;
            app.Label_Member.Layout.Column = [1 2];
            app.Label_Member.Text = '小组成员：卢瑞林、卢柯吉、林芷伊、张昀蕾';

            % Create WelcomeLabel
            app.WelcomeLabel = uilabel(app.GridLayout_Welcome);
            app.WelcomeLabel.HorizontalAlignment = 'center';
            app.WelcomeLabel.FontName = 'Times New Roman';
            app.WelcomeLabel.FontSize = 48;
            app.WelcomeLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.WelcomeLabel.Layout.Row = 1;
            app.WelcomeLabel.Layout.Column = [1 2];
            app.WelcomeLabel.Text = 'Welcome!';

            % Create Image
            app.Image = uiimage(app.GridLayout_Welcome);
            app.Image.Layout.Row = 2;
            app.Image.Layout.Column = 2;
            app.Image.ImageSource = fullfile(pathToMLAPP, 'Figure', 'smith_plot.png');

            % Create Tab_LRight_Home
            app.Tab_LRight_Home = uitab(app.TabGroup);
            app.Tab_LRight_Home.Title = 'L型电路(右)';
            app.Tab_LRight_Home.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_LRight_Home.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout5
            app.GridLayout5 = uigridlayout(app.Tab_LRight_Home);
            app.GridLayout5.ColumnWidth = {'1x'};
            app.GridLayout5.RowHeight = {'1x', '3x'};
            app.GridLayout5.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create GridLayout10
            app.GridLayout10 = uigridlayout(app.GridLayout5);
            app.GridLayout10.Layout.Row = 1;
            app.GridLayout10.Layout.Column = 1;
            app.GridLayout10.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create Image_LRight
            app.Image_LRight = uiimage(app.GridLayout10);
            app.Image_LRight.Layout.Row = [1 2];
            app.Image_LRight.Layout.Column = 1;
            app.Image_LRight.ImageSource = fullfile(pathToMLAPP, 'Figure', 'L_Right.jpg');

            % Create GridLayout11
            app.GridLayout11 = uigridlayout(app.GridLayout10);
            app.GridLayout11.Layout.Row = [1 2];
            app.GridLayout11.Layout.Column = 2;
            app.GridLayout11.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create fmathrmMHzLabel
            app.fmathrmMHzLabel = uilabel(app.GridLayout11);
            app.fmathrmMHzLabel.HorizontalAlignment = 'center';
            app.fmathrmMHzLabel.FontSize = 18;
            app.fmathrmMHzLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.fmathrmMHzLabel.Layout.Row = 1;
            app.fmathrmMHzLabel.Layout.Column = 1;
            app.fmathrmMHzLabel.Interpreter = 'latex';
            app.fmathrmMHzLabel.Text = '工作频率 $f$ / $\mathrm{MHz}$';

            % Create MHzLabel
            app.MHzLabel = uilabel(app.GridLayout11);
            app.MHzLabel.HorizontalAlignment = 'center';
            app.MHzLabel.FontName = 'Times New Roman';
            app.MHzLabel.FontSize = 18;
            app.MHzLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.MHzLabel.Layout.Row = 2;
            app.MHzLabel.Layout.Column = 2;
            app.MHzLabel.Interpreter = 'tex';
            app.MHzLabel.Text = '单位 MHz';

            % Create EditField_Operat_f
            app.EditField_Operat_f = uieditfield(app.GridLayout11, 'numeric');
            app.EditField_Operat_f.Limits = [1 133];
            app.EditField_Operat_f.ValueDisplayFormat = '%.6f';
            app.EditField_Operat_f.FontSize = 18;
            app.EditField_Operat_f.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Operat_f.Layout.Row = 2;
            app.EditField_Operat_f.Layout.Column = 1;
            app.EditField_Operat_f.Value = 1;

            % Create Button_Readme_L_Right
            app.Button_Readme_L_Right = uibutton(app.GridLayout11, 'push');
            app.Button_Readme_L_Right.ButtonPushedFcn = createCallbackFcn(app, @Button_Readme_L_RightPushed, true);
            app.Button_Readme_L_Right.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Readme_L_Right.FontName = 'Times New Roman';
            app.Button_Readme_L_Right.FontSize = 24;
            app.Button_Readme_L_Right.FontWeight = 'bold';
            app.Button_Readme_L_Right.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Readme_L_Right.Layout.Row = 1;
            app.Button_Readme_L_Right.Layout.Column = 2;
            app.Button_Readme_L_Right.Text = 'Read me';

            % Create GridLayout12
            app.GridLayout12 = uigridlayout(app.GridLayout5);
            app.GridLayout12.RowHeight = {'1x', '4x'};
            app.GridLayout12.Layout.Row = 2;
            app.GridLayout12.Layout.Column = 1;
            app.GridLayout12.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create textbfLC_1C_2Z_mathrmloadLabel
            app.textbfLC_1C_2Z_mathrmloadLabel = uilabel(app.GridLayout12);
            app.textbfLC_1C_2Z_mathrmloadLabel.HorizontalAlignment = 'center';
            app.textbfLC_1C_2Z_mathrmloadLabel.WordWrap = 'on';
            app.textbfLC_1C_2Z_mathrmloadLabel.FontSize = 14;
            app.textbfLC_1C_2Z_mathrmloadLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfLC_1C_2Z_mathrmloadLabel.Layout.Row = 1;
            app.textbfLC_1C_2Z_mathrmloadLabel.Layout.Column = 1;
            app.textbfLC_1C_2Z_mathrmloadLabel.Interpreter = 'latex';
            app.textbfLC_1C_2Z_mathrmloadLabel.Text = '\textbf{正向计算}：设置元件参数 $(L, C_1, C_2)$，推导可匹配负载阻抗范围 $(Z_{\mathrm{load}})$';

            % Create textbfZ_mathrmLLC_1C_2Label
            app.textbfZ_mathrmLLC_1C_2Label = uilabel(app.GridLayout12);
            app.textbfZ_mathrmLLC_1C_2Label.HorizontalAlignment = 'center';
            app.textbfZ_mathrmLLC_1C_2Label.WordWrap = 'on';
            app.textbfZ_mathrmLLC_1C_2Label.FontSize = 14;
            app.textbfZ_mathrmLLC_1C_2Label.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfZ_mathrmLLC_1C_2Label.Layout.Row = 1;
            app.textbfZ_mathrmLLC_1C_2Label.Layout.Column = 2;
            app.textbfZ_mathrmLLC_1C_2Label.Interpreter = 'latex';
            app.textbfZ_mathrmLLC_1C_2Label.Text = '\textbf{反向计算}：目标负载阻抗 $Z_{\mathrm{L}}$ + 选定电感 $L$，推导所需电容 $(C_1, C_2)$';

            % Create GridLayout13
            app.GridLayout13 = uigridlayout(app.GridLayout12);
            app.GridLayout13.ColumnWidth = {'1x', '1x', '1x', '1x'};
            app.GridLayout13.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13.Layout.Row = 2;
            app.GridLayout13.Layout.Column = 1;
            app.GridLayout13.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_2
            app.LHLabel_2 = uilabel(app.GridLayout13);
            app.LHLabel_2.HorizontalAlignment = 'center';
            app.LHLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_2.Layout.Row = 1;
            app.LHLabel_2.Layout.Column = 1;
            app.LHLabel_2.Interpreter = 'latex';
            app.LHLabel_2.Text = '电感值$L(μH)$';

            % Create EditField_LRight_Set_L
            app.EditField_LRight_Set_L = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Set_L.Limits = [0 Inf];
            app.EditField_LRight_Set_L.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Set_L.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Set_L.Layout.Row = 1;
            app.EditField_LRight_Set_L.Layout.Column = [2 4];

            % Create C1pFLabel
            app.C1pFLabel = uilabel(app.GridLayout13);
            app.C1pFLabel.HorizontalAlignment = 'center';
            app.C1pFLabel.FontSize = 10;
            app.C1pFLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel.Layout.Row = 3;
            app.C1pFLabel.Layout.Column = 1;
            app.C1pFLabel.Interpreter = 'latex';
            app.C1pFLabel.Text = '电容值$C1(pF)$';

            % Create EditField_LRight_Set_C1_min
            app.EditField_LRight_Set_C1_min = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Set_C1_min.Limits = [0.01 Inf];
            app.EditField_LRight_Set_C1_min.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Set_C1_min.FontSize = 10;
            app.EditField_LRight_Set_C1_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Set_C1_min.Layout.Row = 3;
            app.EditField_LRight_Set_C1_min.Layout.Column = 2;
            app.EditField_LRight_Set_C1_min.Value = 0.01;

            % Create C1pFLabel_2
            app.C1pFLabel_2 = uilabel(app.GridLayout13);
            app.C1pFLabel_2.HorizontalAlignment = 'center';
            app.C1pFLabel_2.FontSize = 10;
            app.C1pFLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_2.Layout.Row = 4;
            app.C1pFLabel_2.Layout.Column = 1;
            app.C1pFLabel_2.Interpreter = 'latex';
            app.C1pFLabel_2.Text = '电容值$C2(pF)$';

            % Create EditField_LRight_Set_C2_min
            app.EditField_LRight_Set_C2_min = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Set_C2_min.Limits = [0.01 Inf];
            app.EditField_LRight_Set_C2_min.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Set_C2_min.FontSize = 9;
            app.EditField_LRight_Set_C2_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Set_C2_min.Layout.Row = 4;
            app.EditField_LRight_Set_C2_min.Layout.Column = 2;
            app.EditField_LRight_Set_C2_min.Value = 0.01;

            % Create Button_LRight_Forward
            app.Button_LRight_Forward = uibutton(app.GridLayout13, 'push');
            app.Button_LRight_Forward.ButtonPushedFcn = createCallbackFcn(app, @Button_LRight_ForwardPushed, true);
            app.Button_LRight_Forward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_LRight_Forward.FontSize = 18;
            app.Button_LRight_Forward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_LRight_Forward.Layout.Row = 5;
            app.Button_LRight_Forward.Layout.Column = [1 4];
            app.Button_LRight_Forward.Text = '正向计算可匹配负载阻抗范围';

            % Create Z_LoadR_LjX_LLabel
            app.Z_LoadR_LjX_LLabel = uilabel(app.GridLayout13);
            app.Z_LoadR_LjX_LLabel.HorizontalAlignment = 'center';
            app.Z_LoadR_LjX_LLabel.FontSize = 14;
            app.Z_LoadR_LjX_LLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_LoadR_LjX_LLabel.Layout.Row = 6;
            app.Z_LoadR_LjX_LLabel.Layout.Column = [1 4];
            app.Z_LoadR_LjX_LLabel.Interpreter = 'latex';
            app.Z_LoadR_LjX_LLabel.Text = '可匹配负载阻抗范围：$Z_{Load} = R_L + jX_L$(单位Ω)';

            % Create Z_Load_minLabel
            app.Z_Load_minLabel = uilabel(app.GridLayout13);
            app.Z_Load_minLabel.HorizontalAlignment = 'center';
            app.Z_Load_minLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel.Layout.Row = 7;
            app.Z_Load_minLabel.Layout.Column = 1;
            app.Z_Load_minLabel.Interpreter = 'latex';
            app.Z_Load_minLabel.Text = '$Z_{Load_{min}} =$';

            % Create EditField_LRight_Cal_Zmin_Real
            app.EditField_LRight_Cal_Zmin_Real = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Cal_Zmin_Real.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Cal_Zmin_Real.Editable = 'off';
            app.EditField_LRight_Cal_Zmin_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Cal_Zmin_Real.Layout.Row = 7;
            app.EditField_LRight_Cal_Zmin_Real.Layout.Column = 2;

            % Create Z_Load_maxLabel
            app.Z_Load_maxLabel = uilabel(app.GridLayout13);
            app.Z_Load_maxLabel.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel.Layout.Row = 8;
            app.Z_Load_maxLabel.Layout.Column = 1;
            app.Z_Load_maxLabel.Interpreter = 'latex';
            app.Z_Load_maxLabel.Text = '$Z_{Load_{max}} =$';

            % Create EditField_LRight_Cal_Zmax_Real
            app.EditField_LRight_Cal_Zmax_Real = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Cal_Zmax_Real.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Cal_Zmax_Real.Editable = 'off';
            app.EditField_LRight_Cal_Zmax_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Cal_Zmax_Real.Layout.Row = 8;
            app.EditField_LRight_Cal_Zmax_Real.Layout.Column = 2;

            % Create EditField_LRight_Set_C1_max
            app.EditField_LRight_Set_C1_max = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Set_C1_max.Limits = [0 Inf];
            app.EditField_LRight_Set_C1_max.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Set_C1_max.FontSize = 10;
            app.EditField_LRight_Set_C1_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Set_C1_max.Layout.Row = 3;
            app.EditField_LRight_Set_C1_max.Layout.Column = 4;

            % Create EditField_LRight_Set_C2_max
            app.EditField_LRight_Set_C2_max = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Set_C2_max.Limits = [0 Inf];
            app.EditField_LRight_Set_C2_max.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Set_C2_max.FontSize = 10;
            app.EditField_LRight_Set_C2_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Set_C2_max.Layout.Row = 4;
            app.EditField_LRight_Set_C2_max.Layout.Column = 4;

            % Create minLabel
            app.minLabel = uilabel(app.GridLayout13);
            app.minLabel.HorizontalAlignment = 'center';
            app.minLabel.FontName = 'Times New Roman';
            app.minLabel.FontSize = 18;
            app.minLabel.FontWeight = 'bold';
            app.minLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.minLabel.Layout.Row = 2;
            app.minLabel.Layout.Column = 2;
            app.minLabel.Text = 'min';

            % Create maxLabel
            app.maxLabel = uilabel(app.GridLayout13);
            app.maxLabel.HorizontalAlignment = 'center';
            app.maxLabel.FontName = 'Times New Roman';
            app.maxLabel.FontSize = 18;
            app.maxLabel.FontWeight = 'bold';
            app.maxLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.maxLabel.Layout.Row = 2;
            app.maxLabel.Layout.Column = 4;
            app.maxLabel.Text = 'max';

            % Create EditField_LRight_Cal_Zmin_Im
            app.EditField_LRight_Cal_Zmin_Im = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Cal_Zmin_Im.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Cal_Zmin_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Cal_Zmin_Im.Layout.Row = 7;
            app.EditField_LRight_Cal_Zmin_Im.Layout.Column = 4;

            % Create EditField_LRight_Cal_Zmax_Im
            app.EditField_LRight_Cal_Zmax_Im = uieditfield(app.GridLayout13, 'numeric');
            app.EditField_LRight_Cal_Zmax_Im.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Cal_Zmax_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Cal_Zmax_Im.Layout.Row = 8;
            app.EditField_LRight_Cal_Zmax_Im.Layout.Column = 4;

            % Create Label
            app.Label = uilabel(app.GridLayout13);
            app.Label.HorizontalAlignment = 'center';
            app.Label.FontSize = 18;
            app.Label.FontWeight = 'bold';
            app.Label.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label.Layout.Row = 3;
            app.Label.Layout.Column = 3;
            app.Label.Text = '~';

            % Create Label_2
            app.Label_2 = uilabel(app.GridLayout13);
            app.Label_2.HorizontalAlignment = 'center';
            app.Label_2.FontSize = 18;
            app.Label_2.FontWeight = 'bold';
            app.Label_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_2.Layout.Row = 4;
            app.Label_2.Layout.Column = 3;
            app.Label_2.Text = '~';

            % Create jLabel_7
            app.jLabel_7 = uilabel(app.GridLayout13);
            app.jLabel_7.HorizontalAlignment = 'center';
            app.jLabel_7.FontName = 'Times New Roman';
            app.jLabel_7.FontSize = 18;
            app.jLabel_7.FontWeight = 'bold';
            app.jLabel_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_7.Layout.Row = 7;
            app.jLabel_7.Layout.Column = 3;
            app.jLabel_7.Text = '+j';

            % Create jLabel_8
            app.jLabel_8 = uilabel(app.GridLayout13);
            app.jLabel_8.HorizontalAlignment = 'center';
            app.jLabel_8.FontName = 'Times New Roman';
            app.jLabel_8.FontSize = 18;
            app.jLabel_8.FontWeight = 'bold';
            app.jLabel_8.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_8.Layout.Row = 8;
            app.jLabel_8.Layout.Column = 3;
            app.jLabel_8.Text = '+j';

            % Create GridLayout13_2
            app.GridLayout13_2 = uigridlayout(app.GridLayout12);
            app.GridLayout13_2.ColumnWidth = {'2x', '1x', '1x', '1x'};
            app.GridLayout13_2.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_2.Layout.Row = 2;
            app.GridLayout13_2.Layout.Column = 2;
            app.GridLayout13_2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel
            app.LHLabel = uilabel(app.GridLayout13_2);
            app.LHLabel.HorizontalAlignment = 'center';
            app.LHLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel.Layout.Row = 1;
            app.LHLabel.Layout.Column = 1;
            app.LHLabel.Interpreter = 'latex';
            app.LHLabel.Text = '选定电感值$L(μH)$';

            % Create EditField_LRight_Set_L_2
            app.EditField_LRight_Set_L_2 = uieditfield(app.GridLayout13_2, 'numeric');
            app.EditField_LRight_Set_L_2.Limits = [0 Inf];
            app.EditField_LRight_Set_L_2.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Set_L_2.FontSize = 10;
            app.EditField_LRight_Set_L_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Set_L_2.Layout.Row = 1;
            app.EditField_LRight_Set_L_2.Layout.Column = [2 4];

            % Create C1pFLabel_3
            app.C1pFLabel_3 = uilabel(app.GridLayout13_2);
            app.C1pFLabel_3.HorizontalAlignment = 'center';
            app.C1pFLabel_3.FontSize = 10;
            app.C1pFLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_3.Layout.Row = 2;
            app.C1pFLabel_3.Layout.Column = 1;
            app.C1pFLabel_3.Interpreter = 'latex';
            app.C1pFLabel_3.Text = '目标负载阻抗 $Z_L$(单位Ω)';

            % Create EditField_LRight_Target_Z_Real
            app.EditField_LRight_Target_Z_Real = uieditfield(app.GridLayout13_2, 'numeric');
            app.EditField_LRight_Target_Z_Real.Limits = [0 50];
            app.EditField_LRight_Target_Z_Real.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Target_Z_Real.FontSize = 10;
            app.EditField_LRight_Target_Z_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Target_Z_Real.Layout.Row = 2;
            app.EditField_LRight_Target_Z_Real.Layout.Column = 2;

            % Create Button_LRight_Backward
            app.Button_LRight_Backward = uibutton(app.GridLayout13_2, 'push');
            app.Button_LRight_Backward.ButtonPushedFcn = createCallbackFcn(app, @Button_LRight_BackwardPushed, true);
            app.Button_LRight_Backward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_LRight_Backward.FontSize = 18;
            app.Button_LRight_Backward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_LRight_Backward.Layout.Row = 3;
            app.Button_LRight_Backward.Layout.Column = [1 4];
            app.Button_LRight_Backward.Text = '反向计算所需电容值';

            % Create C1C2Label
            app.C1C2Label = uilabel(app.GridLayout13_2);
            app.C1C2Label.HorizontalAlignment = 'center';
            app.C1C2Label.FontSize = 14;
            app.C1C2Label.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1C2Label.Layout.Row = 4;
            app.C1C2Label.Layout.Column = [1 4];
            app.C1C2Label.Interpreter = 'latex';
            app.C1C2Label.Text = '所需电容值：$C1、C2$';

            % Create Z_Load_minLabel_2
            app.Z_Load_minLabel_2 = uilabel(app.GridLayout13_2);
            app.Z_Load_minLabel_2.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_2.FontSize = 10;
            app.Z_Load_minLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_2.Layout.Row = 5;
            app.Z_Load_minLabel_2.Layout.Column = 1;
            app.Z_Load_minLabel_2.Interpreter = 'latex';
            app.Z_Load_minLabel_2.Text = '所需电容值$C1(pF)=$';

            % Create EditField_LRight_Cal_C1
            app.EditField_LRight_Cal_C1 = uieditfield(app.GridLayout13_2, 'numeric');
            app.EditField_LRight_Cal_C1.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Cal_C1.Editable = 'off';
            app.EditField_LRight_Cal_C1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Cal_C1.Layout.Row = 5;
            app.EditField_LRight_Cal_C1.Layout.Column = [2 4];

            % Create Z_Load_maxLabel_2
            app.Z_Load_maxLabel_2 = uilabel(app.GridLayout13_2);
            app.Z_Load_maxLabel_2.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_2.FontSize = 10;
            app.Z_Load_maxLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_2.Layout.Row = 6;
            app.Z_Load_maxLabel_2.Layout.Column = 1;
            app.Z_Load_maxLabel_2.Interpreter = 'latex';
            app.Z_Load_maxLabel_2.Text = '所需电容值$C2(pF)=$';

            % Create EditField_LRight_Cal_C2
            app.EditField_LRight_Cal_C2 = uieditfield(app.GridLayout13_2, 'numeric');
            app.EditField_LRight_Cal_C2.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Cal_C2.Editable = 'off';
            app.EditField_LRight_Cal_C2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Cal_C2.Layout.Row = 6;
            app.EditField_LRight_Cal_C2.Layout.Column = [2 4];

            % Create Button_Voltage_Max_LRight
            app.Button_Voltage_Max_LRight = uibutton(app.GridLayout13_2, 'push');
            app.Button_Voltage_Max_LRight.ButtonPushedFcn = createCallbackFcn(app, @Button_Voltage_Max_Pushed, true);
            app.Button_Voltage_Max_LRight.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Voltage_Max_LRight.FontSize = 18;
            app.Button_Voltage_Max_LRight.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Voltage_Max_LRight.Layout.Row = 7;
            app.Button_Voltage_Max_LRight.Layout.Column = [1 4];
            app.Button_Voltage_Max_LRight.Text = '反向计算的元件承压值';

            % Create jEditFieldLabel
            app.jEditFieldLabel = uilabel(app.GridLayout13_2);
            app.jEditFieldLabel.HorizontalAlignment = 'center';
            app.jEditFieldLabel.FontName = 'Times New Roman';
            app.jEditFieldLabel.FontSize = 18;
            app.jEditFieldLabel.FontWeight = 'bold';
            app.jEditFieldLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jEditFieldLabel.Layout.Row = 2;
            app.jEditFieldLabel.Layout.Column = 3;
            app.jEditFieldLabel.Text = '+j';

            % Create EditField_LRight_Target_Z_Im
            app.EditField_LRight_Target_Z_Im = uieditfield(app.GridLayout13_2, 'numeric');
            app.EditField_LRight_Target_Z_Im.ValueDisplayFormat = '%.6f';
            app.EditField_LRight_Target_Z_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LRight_Target_Z_Im.Layout.Row = 2;
            app.EditField_LRight_Target_Z_Im.Layout.Column = 4;

            % Create Tab_LLeft_Home
            app.Tab_LLeft_Home = uitab(app.TabGroup);
            app.Tab_LLeft_Home.Title = 'L型电路(左)';
            app.Tab_LLeft_Home.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_LLeft_Home.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout5_2
            app.GridLayout5_2 = uigridlayout(app.Tab_LLeft_Home);
            app.GridLayout5_2.ColumnWidth = {'1x'};
            app.GridLayout5_2.RowHeight = {'1x', '3x'};
            app.GridLayout5_2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create GridLayout10_2
            app.GridLayout10_2 = uigridlayout(app.GridLayout5_2);
            app.GridLayout10_2.Layout.Row = 1;
            app.GridLayout10_2.Layout.Column = 1;
            app.GridLayout10_2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create Image_LLeft
            app.Image_LLeft = uiimage(app.GridLayout10_2);
            app.Image_LLeft.Layout.Row = [1 2];
            app.Image_LLeft.Layout.Column = 1;
            app.Image_LLeft.ImageSource = fullfile(pathToMLAPP, 'Figure', 'L_Left.jpg');

            % Create GridLayout11_2
            app.GridLayout11_2 = uigridlayout(app.GridLayout10_2);
            app.GridLayout11_2.Layout.Row = [1 2];
            app.GridLayout11_2.Layout.Column = 2;
            app.GridLayout11_2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create fmathrmMHzLabel_2
            app.fmathrmMHzLabel_2 = uilabel(app.GridLayout11_2);
            app.fmathrmMHzLabel_2.HorizontalAlignment = 'center';
            app.fmathrmMHzLabel_2.FontSize = 18;
            app.fmathrmMHzLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.fmathrmMHzLabel_2.Layout.Row = 1;
            app.fmathrmMHzLabel_2.Layout.Column = 1;
            app.fmathrmMHzLabel_2.Interpreter = 'latex';
            app.fmathrmMHzLabel_2.Text = '工作频率 $f$ / $\mathrm{MHz}$';

            % Create MHzLabel_3
            app.MHzLabel_3 = uilabel(app.GridLayout11_2);
            app.MHzLabel_3.HorizontalAlignment = 'center';
            app.MHzLabel_3.FontName = 'Times New Roman';
            app.MHzLabel_3.FontSize = 18;
            app.MHzLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.MHzLabel_3.Layout.Row = 2;
            app.MHzLabel_3.Layout.Column = 2;
            app.MHzLabel_3.Interpreter = 'tex';
            app.MHzLabel_3.Text = '单位 MHz';

            % Create EditField_Operat_f_LLeft
            app.EditField_Operat_f_LLeft = uieditfield(app.GridLayout11_2, 'numeric');
            app.EditField_Operat_f_LLeft.Limits = [1 133];
            app.EditField_Operat_f_LLeft.ValueDisplayFormat = '%.6f';
            app.EditField_Operat_f_LLeft.FontSize = 18;
            app.EditField_Operat_f_LLeft.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Operat_f_LLeft.Layout.Row = 2;
            app.EditField_Operat_f_LLeft.Layout.Column = 1;
            app.EditField_Operat_f_LLeft.Value = 1;

            % Create Button_Readme_L_Left
            app.Button_Readme_L_Left = uibutton(app.GridLayout11_2, 'push');
            app.Button_Readme_L_Left.ButtonPushedFcn = createCallbackFcn(app, @Button_Readme_L_LeftPushed, true);
            app.Button_Readme_L_Left.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Readme_L_Left.FontName = 'Times New Roman';
            app.Button_Readme_L_Left.FontSize = 24;
            app.Button_Readme_L_Left.FontWeight = 'bold';
            app.Button_Readme_L_Left.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Readme_L_Left.Layout.Row = 1;
            app.Button_Readme_L_Left.Layout.Column = 2;
            app.Button_Readme_L_Left.Text = 'Read me';

            % Create GridLayout12_2
            app.GridLayout12_2 = uigridlayout(app.GridLayout5_2);
            app.GridLayout12_2.RowHeight = {'1x', '4x'};
            app.GridLayout12_2.Layout.Row = 2;
            app.GridLayout12_2.Layout.Column = 1;
            app.GridLayout12_2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create textbfLC_1C_2Z_mathrmloadLabel_2
            app.textbfLC_1C_2Z_mathrmloadLabel_2 = uilabel(app.GridLayout12_2);
            app.textbfLC_1C_2Z_mathrmloadLabel_2.HorizontalAlignment = 'center';
            app.textbfLC_1C_2Z_mathrmloadLabel_2.WordWrap = 'on';
            app.textbfLC_1C_2Z_mathrmloadLabel_2.FontSize = 14;
            app.textbfLC_1C_2Z_mathrmloadLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfLC_1C_2Z_mathrmloadLabel_2.Layout.Row = 1;
            app.textbfLC_1C_2Z_mathrmloadLabel_2.Layout.Column = 1;
            app.textbfLC_1C_2Z_mathrmloadLabel_2.Interpreter = 'latex';
            app.textbfLC_1C_2Z_mathrmloadLabel_2.Text = '\textbf{正向计算}：设置元件参数 $(L, C_1, C_2)$，推导可匹配负载阻抗范围 $(Z_{\mathrm{load}})$';

            % Create textbfZ_mathrmLLC_1C_2Label_2
            app.textbfZ_mathrmLLC_1C_2Label_2 = uilabel(app.GridLayout12_2);
            app.textbfZ_mathrmLLC_1C_2Label_2.HorizontalAlignment = 'center';
            app.textbfZ_mathrmLLC_1C_2Label_2.WordWrap = 'on';
            app.textbfZ_mathrmLLC_1C_2Label_2.FontSize = 14;
            app.textbfZ_mathrmLLC_1C_2Label_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfZ_mathrmLLC_1C_2Label_2.Layout.Row = 1;
            app.textbfZ_mathrmLLC_1C_2Label_2.Layout.Column = 2;
            app.textbfZ_mathrmLLC_1C_2Label_2.Interpreter = 'latex';
            app.textbfZ_mathrmLLC_1C_2Label_2.Text = '\textbf{反向计算}：目标负载阻抗 $Z_{\mathrm{L}}$ + 选定电感 $L$，推导所需电容 $(C_1, C_2)$';

            % Create GridLayout13_3
            app.GridLayout13_3 = uigridlayout(app.GridLayout12_2);
            app.GridLayout13_3.ColumnWidth = {'1x', '1x', '1x', '1x'};
            app.GridLayout13_3.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_3.Layout.Row = 2;
            app.GridLayout13_3.Layout.Column = 1;
            app.GridLayout13_3.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_3
            app.LHLabel_3 = uilabel(app.GridLayout13_3);
            app.LHLabel_3.HorizontalAlignment = 'center';
            app.LHLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_3.Layout.Row = 1;
            app.LHLabel_3.Layout.Column = 1;
            app.LHLabel_3.Interpreter = 'latex';
            app.LHLabel_3.Text = '电感值$L(μH)$';

            % Create EditField_LLeft_Set_L_1
            app.EditField_LLeft_Set_L_1 = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Set_L_1.Limits = [0 Inf];
            app.EditField_LLeft_Set_L_1.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Set_L_1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Set_L_1.Layout.Row = 1;
            app.EditField_LLeft_Set_L_1.Layout.Column = [2 4];

            % Create C1pFLabel_4
            app.C1pFLabel_4 = uilabel(app.GridLayout13_3);
            app.C1pFLabel_4.HorizontalAlignment = 'center';
            app.C1pFLabel_4.FontSize = 10;
            app.C1pFLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_4.Layout.Row = 3;
            app.C1pFLabel_4.Layout.Column = 1;
            app.C1pFLabel_4.Interpreter = 'latex';
            app.C1pFLabel_4.Text = '电容值$C1(pF)$';

            % Create EditField_LLeft_Set_C1_min
            app.EditField_LLeft_Set_C1_min = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Set_C1_min.Limits = [0.01 Inf];
            app.EditField_LLeft_Set_C1_min.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Set_C1_min.FontSize = 10;
            app.EditField_LLeft_Set_C1_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Set_C1_min.Layout.Row = 3;
            app.EditField_LLeft_Set_C1_min.Layout.Column = 2;
            app.EditField_LLeft_Set_C1_min.Value = 0.01;

            % Create C1pFLabel_5
            app.C1pFLabel_5 = uilabel(app.GridLayout13_3);
            app.C1pFLabel_5.HorizontalAlignment = 'center';
            app.C1pFLabel_5.FontSize = 10;
            app.C1pFLabel_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_5.Layout.Row = 4;
            app.C1pFLabel_5.Layout.Column = 1;
            app.C1pFLabel_5.Interpreter = 'latex';
            app.C1pFLabel_5.Text = '电容值$C2(pF)$';

            % Create EditField_LLeft_Set_C2_min
            app.EditField_LLeft_Set_C2_min = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Set_C2_min.Limits = [0.01 Inf];
            app.EditField_LLeft_Set_C2_min.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Set_C2_min.FontSize = 9;
            app.EditField_LLeft_Set_C2_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Set_C2_min.Layout.Row = 4;
            app.EditField_LLeft_Set_C2_min.Layout.Column = 2;
            app.EditField_LLeft_Set_C2_min.Value = 0.01;

            % Create Button_LLeft_Forward
            app.Button_LLeft_Forward = uibutton(app.GridLayout13_3, 'push');
            app.Button_LLeft_Forward.ButtonPushedFcn = createCallbackFcn(app, @Button_LLeft_ForwardPushed, true);
            app.Button_LLeft_Forward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_LLeft_Forward.FontSize = 18;
            app.Button_LLeft_Forward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_LLeft_Forward.Layout.Row = 5;
            app.Button_LLeft_Forward.Layout.Column = [1 4];
            app.Button_LLeft_Forward.Text = '正向计算可匹配负载阻抗范围';

            % Create Z_LoadR_LjX_LLabel_2
            app.Z_LoadR_LjX_LLabel_2 = uilabel(app.GridLayout13_3);
            app.Z_LoadR_LjX_LLabel_2.HorizontalAlignment = 'center';
            app.Z_LoadR_LjX_LLabel_2.FontSize = 14;
            app.Z_LoadR_LjX_LLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_LoadR_LjX_LLabel_2.Layout.Row = 6;
            app.Z_LoadR_LjX_LLabel_2.Layout.Column = [1 4];
            app.Z_LoadR_LjX_LLabel_2.Interpreter = 'latex';
            app.Z_LoadR_LjX_LLabel_2.Text = '可匹配负载阻抗范围：$Z_{Load} = R_L + jX_L$(单位Ω)';

            % Create Z_Load_minLabel_3
            app.Z_Load_minLabel_3 = uilabel(app.GridLayout13_3);
            app.Z_Load_minLabel_3.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_3.Layout.Row = 7;
            app.Z_Load_minLabel_3.Layout.Column = 1;
            app.Z_Load_minLabel_3.Interpreter = 'latex';
            app.Z_Load_minLabel_3.Text = '$Z_{Load_{min}} =$';

            % Create EditField_LLeft_Cal_Zmin_Real
            app.EditField_LLeft_Cal_Zmin_Real = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Cal_Zmin_Real.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Cal_Zmin_Real.Editable = 'off';
            app.EditField_LLeft_Cal_Zmin_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Cal_Zmin_Real.Layout.Row = 7;
            app.EditField_LLeft_Cal_Zmin_Real.Layout.Column = 2;

            % Create Z_Load_maxLabel_3
            app.Z_Load_maxLabel_3 = uilabel(app.GridLayout13_3);
            app.Z_Load_maxLabel_3.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_3.Layout.Row = 8;
            app.Z_Load_maxLabel_3.Layout.Column = 1;
            app.Z_Load_maxLabel_3.Interpreter = 'latex';
            app.Z_Load_maxLabel_3.Text = '$Z_{Load_{max}} =$';

            % Create EditField_LLeft_Cal_Zmax_Real
            app.EditField_LLeft_Cal_Zmax_Real = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Cal_Zmax_Real.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Cal_Zmax_Real.Editable = 'off';
            app.EditField_LLeft_Cal_Zmax_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Cal_Zmax_Real.Layout.Row = 8;
            app.EditField_LLeft_Cal_Zmax_Real.Layout.Column = 2;

            % Create EditField_LLeft_Set_C1_max
            app.EditField_LLeft_Set_C1_max = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Set_C1_max.Limits = [0 Inf];
            app.EditField_LLeft_Set_C1_max.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Set_C1_max.FontSize = 10;
            app.EditField_LLeft_Set_C1_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Set_C1_max.Layout.Row = 3;
            app.EditField_LLeft_Set_C1_max.Layout.Column = 4;

            % Create EditField_LLeft_Set_C2_max
            app.EditField_LLeft_Set_C2_max = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Set_C2_max.Limits = [0 Inf];
            app.EditField_LLeft_Set_C2_max.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Set_C2_max.FontSize = 10;
            app.EditField_LLeft_Set_C2_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Set_C2_max.Layout.Row = 4;
            app.EditField_LLeft_Set_C2_max.Layout.Column = 4;

            % Create minLabel_2
            app.minLabel_2 = uilabel(app.GridLayout13_3);
            app.minLabel_2.HorizontalAlignment = 'center';
            app.minLabel_2.FontName = 'Times New Roman';
            app.minLabel_2.FontSize = 18;
            app.minLabel_2.FontWeight = 'bold';
            app.minLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.minLabel_2.Layout.Row = 2;
            app.minLabel_2.Layout.Column = 2;
            app.minLabel_2.Text = 'min';

            % Create maxLabel_2
            app.maxLabel_2 = uilabel(app.GridLayout13_3);
            app.maxLabel_2.HorizontalAlignment = 'center';
            app.maxLabel_2.FontName = 'Times New Roman';
            app.maxLabel_2.FontSize = 18;
            app.maxLabel_2.FontWeight = 'bold';
            app.maxLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.maxLabel_2.Layout.Row = 2;
            app.maxLabel_2.Layout.Column = 4;
            app.maxLabel_2.Text = 'max';

            % Create EditField_LLeft_Cal_Zmin_Im
            app.EditField_LLeft_Cal_Zmin_Im = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Cal_Zmin_Im.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Cal_Zmin_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Cal_Zmin_Im.Layout.Row = 7;
            app.EditField_LLeft_Cal_Zmin_Im.Layout.Column = 4;

            % Create EditField_LLeft_Cal_Zmax_Im
            app.EditField_LLeft_Cal_Zmax_Im = uieditfield(app.GridLayout13_3, 'numeric');
            app.EditField_LLeft_Cal_Zmax_Im.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Cal_Zmax_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Cal_Zmax_Im.Layout.Row = 8;
            app.EditField_LLeft_Cal_Zmax_Im.Layout.Column = 4;

            % Create Label_3
            app.Label_3 = uilabel(app.GridLayout13_3);
            app.Label_3.HorizontalAlignment = 'center';
            app.Label_3.FontSize = 18;
            app.Label_3.FontWeight = 'bold';
            app.Label_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_3.Layout.Row = 3;
            app.Label_3.Layout.Column = 3;
            app.Label_3.Text = '~';

            % Create Label_4
            app.Label_4 = uilabel(app.GridLayout13_3);
            app.Label_4.HorizontalAlignment = 'center';
            app.Label_4.FontSize = 18;
            app.Label_4.FontWeight = 'bold';
            app.Label_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_4.Layout.Row = 4;
            app.Label_4.Layout.Column = 3;
            app.Label_4.Text = '~';

            % Create jLabel_9
            app.jLabel_9 = uilabel(app.GridLayout13_3);
            app.jLabel_9.HorizontalAlignment = 'center';
            app.jLabel_9.FontName = 'Times New Roman';
            app.jLabel_9.FontSize = 18;
            app.jLabel_9.FontWeight = 'bold';
            app.jLabel_9.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_9.Layout.Row = 7;
            app.jLabel_9.Layout.Column = 3;
            app.jLabel_9.Text = '+j';

            % Create jLabel_10
            app.jLabel_10 = uilabel(app.GridLayout13_3);
            app.jLabel_10.HorizontalAlignment = 'center';
            app.jLabel_10.FontName = 'Times New Roman';
            app.jLabel_10.FontSize = 18;
            app.jLabel_10.FontWeight = 'bold';
            app.jLabel_10.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_10.Layout.Row = 8;
            app.jLabel_10.Layout.Column = 3;
            app.jLabel_10.Text = '+j';

            % Create GridLayout13_4
            app.GridLayout13_4 = uigridlayout(app.GridLayout12_2);
            app.GridLayout13_4.ColumnWidth = {'2x', '1x', '1x', '1x'};
            app.GridLayout13_4.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_4.Layout.Row = 2;
            app.GridLayout13_4.Layout.Column = 2;
            app.GridLayout13_4.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_4
            app.LHLabel_4 = uilabel(app.GridLayout13_4);
            app.LHLabel_4.HorizontalAlignment = 'center';
            app.LHLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_4.Layout.Row = 1;
            app.LHLabel_4.Layout.Column = 1;
            app.LHLabel_4.Interpreter = 'latex';
            app.LHLabel_4.Text = '选定电感值$L(μH)$';

            % Create EditField_LLeft_Set_L_2
            app.EditField_LLeft_Set_L_2 = uieditfield(app.GridLayout13_4, 'numeric');
            app.EditField_LLeft_Set_L_2.Limits = [0 Inf];
            app.EditField_LLeft_Set_L_2.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Set_L_2.FontSize = 10;
            app.EditField_LLeft_Set_L_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Set_L_2.Layout.Row = 1;
            app.EditField_LLeft_Set_L_2.Layout.Column = [2 4];

            % Create C1pFLabel_6
            app.C1pFLabel_6 = uilabel(app.GridLayout13_4);
            app.C1pFLabel_6.HorizontalAlignment = 'center';
            app.C1pFLabel_6.FontSize = 10;
            app.C1pFLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_6.Layout.Row = 2;
            app.C1pFLabel_6.Layout.Column = 1;
            app.C1pFLabel_6.Interpreter = 'latex';
            app.C1pFLabel_6.Text = '目标负载阻抗 $Z_L$(单位Ω)';

            % Create EditField_LLeft_Target_Z_Real
            app.EditField_LLeft_Target_Z_Real = uieditfield(app.GridLayout13_4, 'numeric');
            app.EditField_LLeft_Target_Z_Real.Limits = [50 Inf];
            app.EditField_LLeft_Target_Z_Real.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Target_Z_Real.FontSize = 10;
            app.EditField_LLeft_Target_Z_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Target_Z_Real.Layout.Row = 2;
            app.EditField_LLeft_Target_Z_Real.Layout.Column = 2;
            app.EditField_LLeft_Target_Z_Real.Value = 50;

            % Create Button_LLeft_Backward
            app.Button_LLeft_Backward = uibutton(app.GridLayout13_4, 'push');
            app.Button_LLeft_Backward.ButtonPushedFcn = createCallbackFcn(app, @Button_LLeft_BackwardPushed, true);
            app.Button_LLeft_Backward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_LLeft_Backward.FontSize = 18;
            app.Button_LLeft_Backward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_LLeft_Backward.Layout.Row = 3;
            app.Button_LLeft_Backward.Layout.Column = [1 4];
            app.Button_LLeft_Backward.Text = '反向计算所需电容值';

            % Create C1C2Label_2
            app.C1C2Label_2 = uilabel(app.GridLayout13_4);
            app.C1C2Label_2.HorizontalAlignment = 'center';
            app.C1C2Label_2.FontSize = 14;
            app.C1C2Label_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1C2Label_2.Layout.Row = 4;
            app.C1C2Label_2.Layout.Column = [1 4];
            app.C1C2Label_2.Interpreter = 'latex';
            app.C1C2Label_2.Text = '所需电容值：$C1、C2$';

            % Create Z_Load_minLabel_4
            app.Z_Load_minLabel_4 = uilabel(app.GridLayout13_4);
            app.Z_Load_minLabel_4.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_4.FontSize = 10;
            app.Z_Load_minLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_4.Layout.Row = 5;
            app.Z_Load_minLabel_4.Layout.Column = 1;
            app.Z_Load_minLabel_4.Interpreter = 'latex';
            app.Z_Load_minLabel_4.Text = '所需电容值$C1(pF)=$';

            % Create EditField_LLeft_Cal_C1
            app.EditField_LLeft_Cal_C1 = uieditfield(app.GridLayout13_4, 'numeric');
            app.EditField_LLeft_Cal_C1.Limits = [0 Inf];
            app.EditField_LLeft_Cal_C1.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Cal_C1.Editable = 'off';
            app.EditField_LLeft_Cal_C1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Cal_C1.Layout.Row = 5;
            app.EditField_LLeft_Cal_C1.Layout.Column = [2 4];

            % Create Z_Load_maxLabel_4
            app.Z_Load_maxLabel_4 = uilabel(app.GridLayout13_4);
            app.Z_Load_maxLabel_4.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_4.FontSize = 10;
            app.Z_Load_maxLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_4.Layout.Row = 6;
            app.Z_Load_maxLabel_4.Layout.Column = 1;
            app.Z_Load_maxLabel_4.Interpreter = 'latex';
            app.Z_Load_maxLabel_4.Text = '所需电容值$C2(pF)=$';

            % Create EditField_LLeft_Cal_C2
            app.EditField_LLeft_Cal_C2 = uieditfield(app.GridLayout13_4, 'numeric');
            app.EditField_LLeft_Cal_C2.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Cal_C2.Editable = 'off';
            app.EditField_LLeft_Cal_C2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Cal_C2.Layout.Row = 6;
            app.EditField_LLeft_Cal_C2.Layout.Column = [2 4];

            % Create Button_Voltage_Max_LLeft
            app.Button_Voltage_Max_LLeft = uibutton(app.GridLayout13_4, 'push');
            app.Button_Voltage_Max_LLeft.ButtonPushedFcn = createCallbackFcn(app, @Button_Voltage_Max_Pushed, true);
            app.Button_Voltage_Max_LLeft.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Voltage_Max_LLeft.FontSize = 18;
            app.Button_Voltage_Max_LLeft.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Voltage_Max_LLeft.Layout.Row = 7;
            app.Button_Voltage_Max_LLeft.Layout.Column = [1 4];
            app.Button_Voltage_Max_LLeft.Text = '反向计算的元件承压值';

            % Create jEditFieldLabel_2
            app.jEditFieldLabel_2 = uilabel(app.GridLayout13_4);
            app.jEditFieldLabel_2.HorizontalAlignment = 'center';
            app.jEditFieldLabel_2.FontName = 'Times New Roman';
            app.jEditFieldLabel_2.FontSize = 18;
            app.jEditFieldLabel_2.FontWeight = 'bold';
            app.jEditFieldLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jEditFieldLabel_2.Layout.Row = 2;
            app.jEditFieldLabel_2.Layout.Column = 3;
            app.jEditFieldLabel_2.Text = '+j';

            % Create EditField_LLeft_Target_Z_Im
            app.EditField_LLeft_Target_Z_Im = uieditfield(app.GridLayout13_4, 'numeric');
            app.EditField_LLeft_Target_Z_Im.ValueDisplayFormat = '%.6f';
            app.EditField_LLeft_Target_Z_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_LLeft_Target_Z_Im.Layout.Row = 2;
            app.EditField_LLeft_Target_Z_Im.Layout.Column = 4;

            % Create Tab_T_Home
            app.Tab_T_Home = uitab(app.TabGroup);
            app.Tab_T_Home.Title = 'T型电路';
            app.Tab_T_Home.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_T_Home.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout5_3
            app.GridLayout5_3 = uigridlayout(app.Tab_T_Home);
            app.GridLayout5_3.ColumnWidth = {'1x'};
            app.GridLayout5_3.RowHeight = {'1x', '3x'};
            app.GridLayout5_3.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create GridLayout10_3
            app.GridLayout10_3 = uigridlayout(app.GridLayout5_3);
            app.GridLayout10_3.Layout.Row = 1;
            app.GridLayout10_3.Layout.Column = 1;
            app.GridLayout10_3.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create Image_T
            app.Image_T = uiimage(app.GridLayout10_3);
            app.Image_T.Layout.Row = [1 2];
            app.Image_T.Layout.Column = 1;
            app.Image_T.ImageSource = fullfile(pathToMLAPP, 'Figure', 'T.png');

            % Create GridLayout11_3
            app.GridLayout11_3 = uigridlayout(app.GridLayout10_3);
            app.GridLayout11_3.Layout.Row = [1 2];
            app.GridLayout11_3.Layout.Column = 2;
            app.GridLayout11_3.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create fmathrmMHzLabel_3
            app.fmathrmMHzLabel_3 = uilabel(app.GridLayout11_3);
            app.fmathrmMHzLabel_3.HorizontalAlignment = 'center';
            app.fmathrmMHzLabel_3.FontSize = 18;
            app.fmathrmMHzLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.fmathrmMHzLabel_3.Layout.Row = 1;
            app.fmathrmMHzLabel_3.Layout.Column = 1;
            app.fmathrmMHzLabel_3.Interpreter = 'latex';
            app.fmathrmMHzLabel_3.Text = '工作频率 $f$ / $\mathrm{MHz}$';

            % Create MHzLabel_4
            app.MHzLabel_4 = uilabel(app.GridLayout11_3);
            app.MHzLabel_4.HorizontalAlignment = 'center';
            app.MHzLabel_4.FontName = 'Times New Roman';
            app.MHzLabel_4.FontSize = 18;
            app.MHzLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.MHzLabel_4.Layout.Row = 2;
            app.MHzLabel_4.Layout.Column = 2;
            app.MHzLabel_4.Interpreter = 'tex';
            app.MHzLabel_4.Text = '单位 MHz';

            % Create EditField_Operat_f_T
            app.EditField_Operat_f_T = uieditfield(app.GridLayout11_3, 'numeric');
            app.EditField_Operat_f_T.Limits = [1 133];
            app.EditField_Operat_f_T.ValueDisplayFormat = '%.6f';
            app.EditField_Operat_f_T.FontSize = 18;
            app.EditField_Operat_f_T.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Operat_f_T.Layout.Row = 2;
            app.EditField_Operat_f_T.Layout.Column = 1;
            app.EditField_Operat_f_T.Value = 1;

            % Create Button_Readme_T
            app.Button_Readme_T = uibutton(app.GridLayout11_3, 'push');
            app.Button_Readme_T.ButtonPushedFcn = createCallbackFcn(app, @Button_Readme_TPushed, true);
            app.Button_Readme_T.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Readme_T.FontName = 'Times New Roman';
            app.Button_Readme_T.FontSize = 24;
            app.Button_Readme_T.FontWeight = 'bold';
            app.Button_Readme_T.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Readme_T.Layout.Row = 1;
            app.Button_Readme_T.Layout.Column = 2;
            app.Button_Readme_T.Text = 'Read me';

            % Create GridLayout12_3
            app.GridLayout12_3 = uigridlayout(app.GridLayout5_3);
            app.GridLayout12_3.RowHeight = {'1x', '4x'};
            app.GridLayout12_3.Layout.Row = 2;
            app.GridLayout12_3.Layout.Column = 1;
            app.GridLayout12_3.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create textbfLC_1C_2C_3Z_mathrmloadLabel_3
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3 = uilabel(app.GridLayout12_3);
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.HorizontalAlignment = 'center';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.WordWrap = 'on';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.FontSize = 14;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.Layout.Row = 1;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.Layout.Column = 1;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.Interpreter = 'latex';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_3.Text = '\textbf{正向计算}：设置元件参数 $(L, C_1, C_2, C_3)$，推导可匹配负载阻抗范围 $(Z_{\mathrm{load}})$';

            % Create textbfZ_mathrmLLC_3C_1C_2Label
            app.textbfZ_mathrmLLC_3C_1C_2Label = uilabel(app.GridLayout12_3);
            app.textbfZ_mathrmLLC_3C_1C_2Label.HorizontalAlignment = 'center';
            app.textbfZ_mathrmLLC_3C_1C_2Label.WordWrap = 'on';
            app.textbfZ_mathrmLLC_3C_1C_2Label.FontSize = 14;
            app.textbfZ_mathrmLLC_3C_1C_2Label.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfZ_mathrmLLC_3C_1C_2Label.Layout.Row = 1;
            app.textbfZ_mathrmLLC_3C_1C_2Label.Layout.Column = 2;
            app.textbfZ_mathrmLLC_3C_1C_2Label.Interpreter = 'latex';
            app.textbfZ_mathrmLLC_3C_1C_2Label.Text = '\textbf{反向计算}：目标负载阻抗 $Z_{\mathrm{L}}$ + 选定 $L$ + $C_3$，推导所需电容 $(C_1, C_2)$';

            % Create GridLayout13_5
            app.GridLayout13_5 = uigridlayout(app.GridLayout12_3);
            app.GridLayout13_5.ColumnWidth = {'1x', '1x', '1x', '1x'};
            app.GridLayout13_5.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_5.Layout.Row = 2;
            app.GridLayout13_5.Layout.Column = 1;
            app.GridLayout13_5.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_5
            app.LHLabel_5 = uilabel(app.GridLayout13_5);
            app.LHLabel_5.HorizontalAlignment = 'center';
            app.LHLabel_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_5.Layout.Row = 1;
            app.LHLabel_5.Layout.Column = 1;
            app.LHLabel_5.Interpreter = 'latex';
            app.LHLabel_5.Text = '电感值$L(μH)$';

            % Create EditField_T_Set_L_1
            app.EditField_T_Set_L_1 = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Set_L_1.Limits = [0 Inf];
            app.EditField_T_Set_L_1.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_L_1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_L_1.Layout.Row = 1;
            app.EditField_T_Set_L_1.Layout.Column = [2 4];

            % Create C1pFLabel_7
            app.C1pFLabel_7 = uilabel(app.GridLayout13_5);
            app.C1pFLabel_7.HorizontalAlignment = 'center';
            app.C1pFLabel_7.FontSize = 10;
            app.C1pFLabel_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_7.Layout.Row = 3;
            app.C1pFLabel_7.Layout.Column = 1;
            app.C1pFLabel_7.Interpreter = 'latex';
            app.C1pFLabel_7.Text = '电容值$C1(pF)$';

            % Create EditField_T_Set_C1_min
            app.EditField_T_Set_C1_min = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Set_C1_min.Limits = [0.01 Inf];
            app.EditField_T_Set_C1_min.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_C1_min.FontSize = 10;
            app.EditField_T_Set_C1_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_C1_min.Layout.Row = 3;
            app.EditField_T_Set_C1_min.Layout.Column = 2;
            app.EditField_T_Set_C1_min.Value = 0.01;

            % Create C1pFLabel_8
            app.C1pFLabel_8 = uilabel(app.GridLayout13_5);
            app.C1pFLabel_8.HorizontalAlignment = 'center';
            app.C1pFLabel_8.FontSize = 10;
            app.C1pFLabel_8.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_8.Layout.Row = 4;
            app.C1pFLabel_8.Layout.Column = 1;
            app.C1pFLabel_8.Interpreter = 'latex';
            app.C1pFLabel_8.Text = '电容值$C2(pF)$';

            % Create EditField_T_Set_C2_min
            app.EditField_T_Set_C2_min = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Set_C2_min.Limits = [0.01 Inf];
            app.EditField_T_Set_C2_min.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_C2_min.FontSize = 9;
            app.EditField_T_Set_C2_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_C2_min.Layout.Row = 4;
            app.EditField_T_Set_C2_min.Layout.Column = 2;
            app.EditField_T_Set_C2_min.Value = 0.01;

            % Create Button_T_Forward
            app.Button_T_Forward = uibutton(app.GridLayout13_5, 'push');
            app.Button_T_Forward.ButtonPushedFcn = createCallbackFcn(app, @Button_T_ForwardPushed, true);
            app.Button_T_Forward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_T_Forward.FontSize = 14;
            app.Button_T_Forward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_T_Forward.Layout.Row = 6;
            app.Button_T_Forward.Layout.Column = [1 4];
            app.Button_T_Forward.Text = '正向计算可匹配负载阻抗范围';

            % Create Z_LoadR_LjX_LLabel_3
            app.Z_LoadR_LjX_LLabel_3 = uilabel(app.GridLayout13_5);
            app.Z_LoadR_LjX_LLabel_3.HorizontalAlignment = 'center';
            app.Z_LoadR_LjX_LLabel_3.FontSize = 14;
            app.Z_LoadR_LjX_LLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_LoadR_LjX_LLabel_3.Layout.Row = 7;
            app.Z_LoadR_LjX_LLabel_3.Layout.Column = [1 4];
            app.Z_LoadR_LjX_LLabel_3.Interpreter = 'latex';
            app.Z_LoadR_LjX_LLabel_3.Text = '可匹配负载阻抗范围：$Z_{Load} = R_L + jX_L$(单位Ω)';

            % Create Z_Load_minLabel_5
            app.Z_Load_minLabel_5 = uilabel(app.GridLayout13_5);
            app.Z_Load_minLabel_5.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_5.Layout.Row = 8;
            app.Z_Load_minLabel_5.Layout.Column = 1;
            app.Z_Load_minLabel_5.Interpreter = 'latex';
            app.Z_Load_minLabel_5.Text = '$Z_{Load_{min}} =$';

            % Create EditField_T_Cal_Zmin_Real
            app.EditField_T_Cal_Zmin_Real = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Cal_Zmin_Real.ValueDisplayFormat = '%.6f';
            app.EditField_T_Cal_Zmin_Real.Editable = 'off';
            app.EditField_T_Cal_Zmin_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Cal_Zmin_Real.Layout.Row = 8;
            app.EditField_T_Cal_Zmin_Real.Layout.Column = 2;

            % Create Z_Load_maxLabel_5
            app.Z_Load_maxLabel_5 = uilabel(app.GridLayout13_5);
            app.Z_Load_maxLabel_5.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_5.Layout.Row = 9;
            app.Z_Load_maxLabel_5.Layout.Column = 1;
            app.Z_Load_maxLabel_5.Interpreter = 'latex';
            app.Z_Load_maxLabel_5.Text = '$Z_{Load_{max}} =$';

            % Create EditField_T_Cal_Zmax_Real
            app.EditField_T_Cal_Zmax_Real = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Cal_Zmax_Real.ValueDisplayFormat = '%.6f';
            app.EditField_T_Cal_Zmax_Real.Editable = 'off';
            app.EditField_T_Cal_Zmax_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Cal_Zmax_Real.Layout.Row = 9;
            app.EditField_T_Cal_Zmax_Real.Layout.Column = 2;

            % Create EditField_T_Set_C1_max
            app.EditField_T_Set_C1_max = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Set_C1_max.Limits = [0 Inf];
            app.EditField_T_Set_C1_max.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_C1_max.FontSize = 10;
            app.EditField_T_Set_C1_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_C1_max.Layout.Row = 3;
            app.EditField_T_Set_C1_max.Layout.Column = 4;

            % Create EditField_T_Set_C2_max
            app.EditField_T_Set_C2_max = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Set_C2_max.Limits = [0 Inf];
            app.EditField_T_Set_C2_max.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_C2_max.FontSize = 10;
            app.EditField_T_Set_C2_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_C2_max.Layout.Row = 4;
            app.EditField_T_Set_C2_max.Layout.Column = 4;

            % Create minLabel_3
            app.minLabel_3 = uilabel(app.GridLayout13_5);
            app.minLabel_3.HorizontalAlignment = 'center';
            app.minLabel_3.FontName = 'Times New Roman';
            app.minLabel_3.FontSize = 18;
            app.minLabel_3.FontWeight = 'bold';
            app.minLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.minLabel_3.Layout.Row = 2;
            app.minLabel_3.Layout.Column = 2;
            app.minLabel_3.Text = 'min';

            % Create maxLabel_3
            app.maxLabel_3 = uilabel(app.GridLayout13_5);
            app.maxLabel_3.HorizontalAlignment = 'center';
            app.maxLabel_3.FontName = 'Times New Roman';
            app.maxLabel_3.FontSize = 18;
            app.maxLabel_3.FontWeight = 'bold';
            app.maxLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.maxLabel_3.Layout.Row = 2;
            app.maxLabel_3.Layout.Column = 4;
            app.maxLabel_3.Text = 'max';

            % Create EditField_T_Cal_Zmin_Im
            app.EditField_T_Cal_Zmin_Im = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Cal_Zmin_Im.ValueDisplayFormat = '%.6f';
            app.EditField_T_Cal_Zmin_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Cal_Zmin_Im.Layout.Row = 8;
            app.EditField_T_Cal_Zmin_Im.Layout.Column = 4;

            % Create EditField_T_Cal_Zmax_Im
            app.EditField_T_Cal_Zmax_Im = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Cal_Zmax_Im.ValueDisplayFormat = '%.6f';
            app.EditField_T_Cal_Zmax_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Cal_Zmax_Im.Layout.Row = 9;
            app.EditField_T_Cal_Zmax_Im.Layout.Column = 4;

            % Create Label_5
            app.Label_5 = uilabel(app.GridLayout13_5);
            app.Label_5.HorizontalAlignment = 'center';
            app.Label_5.FontSize = 18;
            app.Label_5.FontWeight = 'bold';
            app.Label_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_5.Layout.Row = 3;
            app.Label_5.Layout.Column = 3;
            app.Label_5.Text = '~';

            % Create Label_6
            app.Label_6 = uilabel(app.GridLayout13_5);
            app.Label_6.HorizontalAlignment = 'center';
            app.Label_6.FontSize = 18;
            app.Label_6.FontWeight = 'bold';
            app.Label_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_6.Layout.Row = 4;
            app.Label_6.Layout.Column = 3;
            app.Label_6.Text = '~';

            % Create jLabel_11
            app.jLabel_11 = uilabel(app.GridLayout13_5);
            app.jLabel_11.HorizontalAlignment = 'center';
            app.jLabel_11.FontName = 'Times New Roman';
            app.jLabel_11.FontSize = 18;
            app.jLabel_11.FontWeight = 'bold';
            app.jLabel_11.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_11.Layout.Row = 8;
            app.jLabel_11.Layout.Column = 3;
            app.jLabel_11.Text = '+j';

            % Create jLabel_12
            app.jLabel_12 = uilabel(app.GridLayout13_5);
            app.jLabel_12.HorizontalAlignment = 'center';
            app.jLabel_12.FontName = 'Times New Roman';
            app.jLabel_12.FontSize = 18;
            app.jLabel_12.FontWeight = 'bold';
            app.jLabel_12.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_12.Layout.Row = 9;
            app.jLabel_12.Layout.Column = 3;
            app.jLabel_12.Text = '+j';

            % Create C1pFLabel_10
            app.C1pFLabel_10 = uilabel(app.GridLayout13_5);
            app.C1pFLabel_10.HorizontalAlignment = 'center';
            app.C1pFLabel_10.FontSize = 10;
            app.C1pFLabel_10.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_10.Layout.Row = 5;
            app.C1pFLabel_10.Layout.Column = 1;
            app.C1pFLabel_10.Interpreter = 'latex';
            app.C1pFLabel_10.Text = '电容值$C3(pF)$';

            % Create EditField_T_Set_C3_min
            app.EditField_T_Set_C3_min = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Set_C3_min.Limits = [0.01 Inf];
            app.EditField_T_Set_C3_min.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_C3_min.FontSize = 9;
            app.EditField_T_Set_C3_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_C3_min.Layout.Row = 5;
            app.EditField_T_Set_C3_min.Layout.Column = 2;
            app.EditField_T_Set_C3_min.Value = 0.01;

            % Create Label_7
            app.Label_7 = uilabel(app.GridLayout13_5);
            app.Label_7.HorizontalAlignment = 'center';
            app.Label_7.FontSize = 18;
            app.Label_7.FontWeight = 'bold';
            app.Label_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_7.Layout.Row = 5;
            app.Label_7.Layout.Column = 3;
            app.Label_7.Text = '~';

            % Create EditField_T_Set_C3_max
            app.EditField_T_Set_C3_max = uieditfield(app.GridLayout13_5, 'numeric');
            app.EditField_T_Set_C3_max.Limits = [0 Inf];
            app.EditField_T_Set_C3_max.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_C3_max.FontSize = 10;
            app.EditField_T_Set_C3_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_C3_max.Layout.Row = 5;
            app.EditField_T_Set_C3_max.Layout.Column = 4;

            % Create GridLayout13_6
            app.GridLayout13_6 = uigridlayout(app.GridLayout12_3);
            app.GridLayout13_6.ColumnWidth = {'2x', '1x', '1x', '1x'};
            app.GridLayout13_6.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_6.Layout.Row = 2;
            app.GridLayout13_6.Layout.Column = 2;
            app.GridLayout13_6.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_6
            app.LHLabel_6 = uilabel(app.GridLayout13_6);
            app.LHLabel_6.HorizontalAlignment = 'center';
            app.LHLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_6.Layout.Row = 1;
            app.LHLabel_6.Layout.Column = 1;
            app.LHLabel_6.Interpreter = 'latex';
            app.LHLabel_6.Text = '选定电感值$L(μH)$';

            % Create EditField_T_Set_L_2
            app.EditField_T_Set_L_2 = uieditfield(app.GridLayout13_6, 'numeric');
            app.EditField_T_Set_L_2.Limits = [0 Inf];
            app.EditField_T_Set_L_2.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_L_2.FontSize = 10;
            app.EditField_T_Set_L_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_L_2.Layout.Row = 1;
            app.EditField_T_Set_L_2.Layout.Column = [2 4];

            % Create C1pFLabel_9
            app.C1pFLabel_9 = uilabel(app.GridLayout13_6);
            app.C1pFLabel_9.HorizontalAlignment = 'center';
            app.C1pFLabel_9.FontSize = 10;
            app.C1pFLabel_9.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_9.Layout.Row = 2;
            app.C1pFLabel_9.Layout.Column = 1;
            app.C1pFLabel_9.Interpreter = 'latex';
            app.C1pFLabel_9.Text = '目标负载阻抗 $Z_L$(单位Ω)';

            % Create EditField_T_Target_Z_Real
            app.EditField_T_Target_Z_Real = uieditfield(app.GridLayout13_6, 'numeric');
            app.EditField_T_Target_Z_Real.Limits = [0 Inf];
            app.EditField_T_Target_Z_Real.ValueDisplayFormat = '%.6f';
            app.EditField_T_Target_Z_Real.FontSize = 10;
            app.EditField_T_Target_Z_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Target_Z_Real.Layout.Row = 2;
            app.EditField_T_Target_Z_Real.Layout.Column = 2;
            app.EditField_T_Target_Z_Real.Value = 50;

            % Create Button_T_Backward
            app.Button_T_Backward = uibutton(app.GridLayout13_6, 'push');
            app.Button_T_Backward.ButtonPushedFcn = createCallbackFcn(app, @Button_T_BackwardPushed, true);
            app.Button_T_Backward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_T_Backward.FontSize = 18;
            app.Button_T_Backward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_T_Backward.Layout.Row = 4;
            app.Button_T_Backward.Layout.Column = [1 4];
            app.Button_T_Backward.Text = '反向计算所需电容值';

            % Create C1C2Label_3
            app.C1C2Label_3 = uilabel(app.GridLayout13_6);
            app.C1C2Label_3.HorizontalAlignment = 'center';
            app.C1C2Label_3.FontSize = 14;
            app.C1C2Label_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1C2Label_3.Layout.Row = 5;
            app.C1C2Label_3.Layout.Column = [1 4];
            app.C1C2Label_3.Interpreter = 'latex';
            app.C1C2Label_3.Text = '所需电容值：$C1、C2$';

            % Create Z_Load_minLabel_6
            app.Z_Load_minLabel_6 = uilabel(app.GridLayout13_6);
            app.Z_Load_minLabel_6.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_6.FontSize = 10;
            app.Z_Load_minLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_6.Layout.Row = 6;
            app.Z_Load_minLabel_6.Layout.Column = 1;
            app.Z_Load_minLabel_6.Interpreter = 'latex';
            app.Z_Load_minLabel_6.Text = '所需电容值$C1(pF)=$';

            % Create EditField_T_Cal_C1
            app.EditField_T_Cal_C1 = uieditfield(app.GridLayout13_6, 'numeric');
            app.EditField_T_Cal_C1.ValueDisplayFormat = '%.6f';
            app.EditField_T_Cal_C1.Editable = 'off';
            app.EditField_T_Cal_C1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Cal_C1.Layout.Row = 6;
            app.EditField_T_Cal_C1.Layout.Column = [2 4];

            % Create Z_Load_maxLabel_6
            app.Z_Load_maxLabel_6 = uilabel(app.GridLayout13_6);
            app.Z_Load_maxLabel_6.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_6.FontSize = 10;
            app.Z_Load_maxLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_6.Layout.Row = 7;
            app.Z_Load_maxLabel_6.Layout.Column = 1;
            app.Z_Load_maxLabel_6.Interpreter = 'latex';
            app.Z_Load_maxLabel_6.Text = '所需电容值$C2(pF)=$';

            % Create EditField_T_Cal_C2
            app.EditField_T_Cal_C2 = uieditfield(app.GridLayout13_6, 'numeric');
            app.EditField_T_Cal_C2.ValueDisplayFormat = '%.6f';
            app.EditField_T_Cal_C2.Editable = 'off';
            app.EditField_T_Cal_C2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Cal_C2.Layout.Row = 7;
            app.EditField_T_Cal_C2.Layout.Column = [2 4];

            % Create Button_Voltage_Max_T
            app.Button_Voltage_Max_T = uibutton(app.GridLayout13_6, 'push');
            app.Button_Voltage_Max_T.ButtonPushedFcn = createCallbackFcn(app, @Button_Voltage_Max_Pushed, true);
            app.Button_Voltage_Max_T.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Voltage_Max_T.FontSize = 18;
            app.Button_Voltage_Max_T.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Voltage_Max_T.Layout.Row = 8;
            app.Button_Voltage_Max_T.Layout.Column = [1 4];
            app.Button_Voltage_Max_T.Text = '反向计算的元件承压值';

            % Create jEditFieldLabel_3
            app.jEditFieldLabel_3 = uilabel(app.GridLayout13_6);
            app.jEditFieldLabel_3.HorizontalAlignment = 'center';
            app.jEditFieldLabel_3.FontName = 'Times New Roman';
            app.jEditFieldLabel_3.FontSize = 18;
            app.jEditFieldLabel_3.FontWeight = 'bold';
            app.jEditFieldLabel_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jEditFieldLabel_3.Layout.Row = 2;
            app.jEditFieldLabel_3.Layout.Column = 3;
            app.jEditFieldLabel_3.Text = '+j';

            % Create EditField_T_Target_Z_Im
            app.EditField_T_Target_Z_Im = uieditfield(app.GridLayout13_6, 'numeric');
            app.EditField_T_Target_Z_Im.ValueDisplayFormat = '%.6f';
            app.EditField_T_Target_Z_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Target_Z_Im.Layout.Row = 2;
            app.EditField_T_Target_Z_Im.Layout.Column = 4;

            % Create Z_Load_minLabel_11
            app.Z_Load_minLabel_11 = uilabel(app.GridLayout13_6);
            app.Z_Load_minLabel_11.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_11.FontSize = 10;
            app.Z_Load_minLabel_11.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_11.Layout.Row = 3;
            app.Z_Load_minLabel_11.Layout.Column = 1;
            app.Z_Load_minLabel_11.Interpreter = 'latex';
            app.Z_Load_minLabel_11.Text = '选定电容值$C3(pF)=$';

            % Create EditField_T_Set_C3
            app.EditField_T_Set_C3 = uieditfield(app.GridLayout13_6, 'numeric');
            app.EditField_T_Set_C3.Limits = [0 Inf];
            app.EditField_T_Set_C3.ValueDisplayFormat = '%.6f';
            app.EditField_T_Set_C3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_T_Set_C3.Layout.Row = 3;
            app.EditField_T_Set_C3.Layout.Column = [2 4];

            % Create Tab_pi1_Home
            app.Tab_pi1_Home = uitab(app.TabGroup);
            app.Tab_pi1_Home.Title = 'pi型电路 Ⅰ';
            app.Tab_pi1_Home.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_pi1_Home.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout5_6
            app.GridLayout5_6 = uigridlayout(app.Tab_pi1_Home);
            app.GridLayout5_6.ColumnWidth = {'1x'};
            app.GridLayout5_6.RowHeight = {'1x', '3x'};
            app.GridLayout5_6.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create GridLayout10_6
            app.GridLayout10_6 = uigridlayout(app.GridLayout5_6);
            app.GridLayout10_6.Layout.Row = 1;
            app.GridLayout10_6.Layout.Column = 1;
            app.GridLayout10_6.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create Image_pi1
            app.Image_pi1 = uiimage(app.GridLayout10_6);
            app.Image_pi1.Layout.Row = [1 2];
            app.Image_pi1.Layout.Column = 1;
            app.Image_pi1.ImageSource = fullfile(pathToMLAPP, 'Figure', 'pi1.png');

            % Create GridLayout11_6
            app.GridLayout11_6 = uigridlayout(app.GridLayout10_6);
            app.GridLayout11_6.Layout.Row = [1 2];
            app.GridLayout11_6.Layout.Column = 2;
            app.GridLayout11_6.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create fmathrmMHzLabel_4
            app.fmathrmMHzLabel_4 = uilabel(app.GridLayout11_6);
            app.fmathrmMHzLabel_4.HorizontalAlignment = 'center';
            app.fmathrmMHzLabel_4.FontSize = 18;
            app.fmathrmMHzLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.fmathrmMHzLabel_4.Layout.Row = 1;
            app.fmathrmMHzLabel_4.Layout.Column = 1;
            app.fmathrmMHzLabel_4.Interpreter = 'latex';
            app.fmathrmMHzLabel_4.Text = '工作频率 $f$ / $\mathrm{MHz}$';

            % Create MHzLabel_7
            app.MHzLabel_7 = uilabel(app.GridLayout11_6);
            app.MHzLabel_7.HorizontalAlignment = 'center';
            app.MHzLabel_7.FontName = 'Times New Roman';
            app.MHzLabel_7.FontSize = 18;
            app.MHzLabel_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.MHzLabel_7.Layout.Row = 2;
            app.MHzLabel_7.Layout.Column = 2;
            app.MHzLabel_7.Interpreter = 'tex';
            app.MHzLabel_7.Text = '单位 MHz';

            % Create EditField_Operat_f_pi1
            app.EditField_Operat_f_pi1 = uieditfield(app.GridLayout11_6, 'numeric');
            app.EditField_Operat_f_pi1.Limits = [1 133];
            app.EditField_Operat_f_pi1.ValueDisplayFormat = '%.6f';
            app.EditField_Operat_f_pi1.FontSize = 18;
            app.EditField_Operat_f_pi1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Operat_f_pi1.Layout.Row = 2;
            app.EditField_Operat_f_pi1.Layout.Column = 1;
            app.EditField_Operat_f_pi1.Value = 1;

            % Create Button_Readme_pi1
            app.Button_Readme_pi1 = uibutton(app.GridLayout11_6, 'push');
            app.Button_Readme_pi1.ButtonPushedFcn = createCallbackFcn(app, @Button_Readme_pi1Pushed, true);
            app.Button_Readme_pi1.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Readme_pi1.FontName = 'Times New Roman';
            app.Button_Readme_pi1.FontSize = 24;
            app.Button_Readme_pi1.FontWeight = 'bold';
            app.Button_Readme_pi1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Readme_pi1.Layout.Row = 1;
            app.Button_Readme_pi1.Layout.Column = 2;
            app.Button_Readme_pi1.Text = 'Read me';

            % Create GridLayout12_6
            app.GridLayout12_6 = uigridlayout(app.GridLayout5_6);
            app.GridLayout12_6.RowHeight = {'1x', '4x'};
            app.GridLayout12_6.Layout.Row = 2;
            app.GridLayout12_6.Layout.Column = 1;
            app.GridLayout12_6.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create textbfLC_1C_2C_3Z_mathrmloadLabel_4
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4 = uilabel(app.GridLayout12_6);
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.HorizontalAlignment = 'center';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.WordWrap = 'on';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.FontSize = 14;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.Layout.Row = 1;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.Layout.Column = 1;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.Interpreter = 'latex';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_4.Text = '\textbf{正向计算}：设置元件参数 $(L, C_1, C_2, C_3)$，推导可匹配负载阻抗范围 $(Z_{\mathrm{load}})$';

            % Create textbfZ_mathrmLLC_3C_1C_2Label_2
            app.textbfZ_mathrmLLC_3C_1C_2Label_2 = uilabel(app.GridLayout12_6);
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.HorizontalAlignment = 'center';
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.WordWrap = 'on';
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.FontSize = 14;
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.Layout.Row = 1;
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.Layout.Column = 2;
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.Interpreter = 'latex';
            app.textbfZ_mathrmLLC_3C_1C_2Label_2.Text = '\textbf{反向计算}：目标负载阻抗 $Z_{\mathrm{L}}$ + 选定 $L$ + $C_3$，推导所需电容 $(C_1, C_2)$';

            % Create GridLayout13_11
            app.GridLayout13_11 = uigridlayout(app.GridLayout12_6);
            app.GridLayout13_11.ColumnWidth = {'1x', '1x', '1x', '1x'};
            app.GridLayout13_11.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_11.Layout.Row = 2;
            app.GridLayout13_11.Layout.Column = 1;
            app.GridLayout13_11.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_15
            app.LHLabel_15 = uilabel(app.GridLayout13_11);
            app.LHLabel_15.HorizontalAlignment = 'center';
            app.LHLabel_15.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_15.Layout.Row = 1;
            app.LHLabel_15.Layout.Column = 1;
            app.LHLabel_15.Interpreter = 'latex';
            app.LHLabel_15.Text = '电感值$L(μH)$';

            % Create EditField_pi1_Set_L
            app.EditField_pi1_Set_L = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Set_L.Limits = [0 Inf];
            app.EditField_pi1_Set_L.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_L.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_L.Layout.Row = 1;
            app.EditField_pi1_Set_L.Layout.Column = [2 4];

            % Create C1pFLabel_19
            app.C1pFLabel_19 = uilabel(app.GridLayout13_11);
            app.C1pFLabel_19.HorizontalAlignment = 'center';
            app.C1pFLabel_19.FontSize = 10;
            app.C1pFLabel_19.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_19.Layout.Row = 3;
            app.C1pFLabel_19.Layout.Column = 1;
            app.C1pFLabel_19.Interpreter = 'latex';
            app.C1pFLabel_19.Text = '电容值$C1(pF)$';

            % Create EditField_pi1_Set_C1_min
            app.EditField_pi1_Set_C1_min = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Set_C1_min.Limits = [0.01 Inf];
            app.EditField_pi1_Set_C1_min.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_C1_min.FontSize = 10;
            app.EditField_pi1_Set_C1_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_C1_min.Layout.Row = 3;
            app.EditField_pi1_Set_C1_min.Layout.Column = 2;
            app.EditField_pi1_Set_C1_min.Value = 0.01;

            % Create C1pFLabel_20
            app.C1pFLabel_20 = uilabel(app.GridLayout13_11);
            app.C1pFLabel_20.HorizontalAlignment = 'center';
            app.C1pFLabel_20.FontSize = 10;
            app.C1pFLabel_20.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_20.Layout.Row = 4;
            app.C1pFLabel_20.Layout.Column = 1;
            app.C1pFLabel_20.Interpreter = 'latex';
            app.C1pFLabel_20.Text = '电容值$C2(pF)$';

            % Create EditField_pi1_Set_C2_min
            app.EditField_pi1_Set_C2_min = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Set_C2_min.Limits = [0.01 Inf];
            app.EditField_pi1_Set_C2_min.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_C2_min.FontSize = 9;
            app.EditField_pi1_Set_C2_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_C2_min.Layout.Row = 4;
            app.EditField_pi1_Set_C2_min.Layout.Column = 2;
            app.EditField_pi1_Set_C2_min.Value = 0.01;

            % Create Button_pi1_Forward
            app.Button_pi1_Forward = uibutton(app.GridLayout13_11, 'push');
            app.Button_pi1_Forward.ButtonPushedFcn = createCallbackFcn(app, @Button_pi1_ForwardPushed, true);
            app.Button_pi1_Forward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_pi1_Forward.FontSize = 14;
            app.Button_pi1_Forward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_pi1_Forward.Layout.Row = 6;
            app.Button_pi1_Forward.Layout.Column = [1 4];
            app.Button_pi1_Forward.Text = '正向计算可匹配负载阻抗范围';

            % Create Z_LoadR_LjX_LLabel_6
            app.Z_LoadR_LjX_LLabel_6 = uilabel(app.GridLayout13_11);
            app.Z_LoadR_LjX_LLabel_6.HorizontalAlignment = 'center';
            app.Z_LoadR_LjX_LLabel_6.FontSize = 14;
            app.Z_LoadR_LjX_LLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_LoadR_LjX_LLabel_6.Layout.Row = 7;
            app.Z_LoadR_LjX_LLabel_6.Layout.Column = [1 4];
            app.Z_LoadR_LjX_LLabel_6.Interpreter = 'latex';
            app.Z_LoadR_LjX_LLabel_6.Text = '可匹配负载阻抗范围：$Z_{Load} = R_L + jX_L$(单位Ω)';

            % Create Z_Load_minLabel_12
            app.Z_Load_minLabel_12 = uilabel(app.GridLayout13_11);
            app.Z_Load_minLabel_12.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_12.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_12.Layout.Row = 8;
            app.Z_Load_minLabel_12.Layout.Column = 1;
            app.Z_Load_minLabel_12.Interpreter = 'latex';
            app.Z_Load_minLabel_12.Text = '$Z_{Load_{min}} =$';

            % Create EditField_pi1_Cal_Zmin_Real
            app.EditField_pi1_Cal_Zmin_Real = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Cal_Zmin_Real.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Cal_Zmin_Real.Editable = 'off';
            app.EditField_pi1_Cal_Zmin_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Cal_Zmin_Real.Layout.Row = 8;
            app.EditField_pi1_Cal_Zmin_Real.Layout.Column = 2;

            % Create Z_Load_maxLabel_11
            app.Z_Load_maxLabel_11 = uilabel(app.GridLayout13_11);
            app.Z_Load_maxLabel_11.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_11.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_11.Layout.Row = 9;
            app.Z_Load_maxLabel_11.Layout.Column = 1;
            app.Z_Load_maxLabel_11.Interpreter = 'latex';
            app.Z_Load_maxLabel_11.Text = '$Z_{Load_{max}} =$';

            % Create EditField_pi1_Cal_Zmax_Real
            app.EditField_pi1_Cal_Zmax_Real = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Cal_Zmax_Real.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Cal_Zmax_Real.Editable = 'off';
            app.EditField_pi1_Cal_Zmax_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Cal_Zmax_Real.Layout.Row = 9;
            app.EditField_pi1_Cal_Zmax_Real.Layout.Column = 2;

            % Create EditField_pi1_Set_C1_max
            app.EditField_pi1_Set_C1_max = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Set_C1_max.Limits = [0 Inf];
            app.EditField_pi1_Set_C1_max.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_C1_max.FontSize = 10;
            app.EditField_pi1_Set_C1_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_C1_max.Layout.Row = 3;
            app.EditField_pi1_Set_C1_max.Layout.Column = 4;

            % Create EditField_pi1_Set_C2_max
            app.EditField_pi1_Set_C2_max = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Set_C2_max.Limits = [0 Inf];
            app.EditField_pi1_Set_C2_max.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_C2_max.FontSize = 10;
            app.EditField_pi1_Set_C2_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_C2_max.Layout.Row = 4;
            app.EditField_pi1_Set_C2_max.Layout.Column = 4;

            % Create minLabel_6
            app.minLabel_6 = uilabel(app.GridLayout13_11);
            app.minLabel_6.HorizontalAlignment = 'center';
            app.minLabel_6.FontName = 'Times New Roman';
            app.minLabel_6.FontSize = 18;
            app.minLabel_6.FontWeight = 'bold';
            app.minLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.minLabel_6.Layout.Row = 2;
            app.minLabel_6.Layout.Column = 2;
            app.minLabel_6.Text = 'min';

            % Create maxLabel_6
            app.maxLabel_6 = uilabel(app.GridLayout13_11);
            app.maxLabel_6.HorizontalAlignment = 'center';
            app.maxLabel_6.FontName = 'Times New Roman';
            app.maxLabel_6.FontSize = 18;
            app.maxLabel_6.FontWeight = 'bold';
            app.maxLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.maxLabel_6.Layout.Row = 2;
            app.maxLabel_6.Layout.Column = 4;
            app.maxLabel_6.Text = 'max';

            % Create EditField_pi1_Cal_Zmin_Im
            app.EditField_pi1_Cal_Zmin_Im = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Cal_Zmin_Im.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Cal_Zmin_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Cal_Zmin_Im.Layout.Row = 8;
            app.EditField_pi1_Cal_Zmin_Im.Layout.Column = 4;

            % Create EditField_pi1_Cal_Zmax_Im
            app.EditField_pi1_Cal_Zmax_Im = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Cal_Zmax_Im.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Cal_Zmax_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Cal_Zmax_Im.Layout.Row = 9;
            app.EditField_pi1_Cal_Zmax_Im.Layout.Column = 4;

            % Create Label_14
            app.Label_14 = uilabel(app.GridLayout13_11);
            app.Label_14.HorizontalAlignment = 'center';
            app.Label_14.FontSize = 18;
            app.Label_14.FontWeight = 'bold';
            app.Label_14.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_14.Layout.Row = 3;
            app.Label_14.Layout.Column = 3;
            app.Label_14.Text = '~';

            % Create Label_15
            app.Label_15 = uilabel(app.GridLayout13_11);
            app.Label_15.HorizontalAlignment = 'center';
            app.Label_15.FontSize = 18;
            app.Label_15.FontWeight = 'bold';
            app.Label_15.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_15.Layout.Row = 4;
            app.Label_15.Layout.Column = 3;
            app.Label_15.Text = '~';

            % Create jLabel_17
            app.jLabel_17 = uilabel(app.GridLayout13_11);
            app.jLabel_17.HorizontalAlignment = 'center';
            app.jLabel_17.FontName = 'Times New Roman';
            app.jLabel_17.FontSize = 18;
            app.jLabel_17.FontWeight = 'bold';
            app.jLabel_17.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_17.Layout.Row = 8;
            app.jLabel_17.Layout.Column = 3;
            app.jLabel_17.Text = '+j';

            % Create jLabel_18
            app.jLabel_18 = uilabel(app.GridLayout13_11);
            app.jLabel_18.HorizontalAlignment = 'center';
            app.jLabel_18.FontName = 'Times New Roman';
            app.jLabel_18.FontSize = 18;
            app.jLabel_18.FontWeight = 'bold';
            app.jLabel_18.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_18.Layout.Row = 9;
            app.jLabel_18.Layout.Column = 3;
            app.jLabel_18.Text = '+j';

            % Create C1pFLabel_21
            app.C1pFLabel_21 = uilabel(app.GridLayout13_11);
            app.C1pFLabel_21.HorizontalAlignment = 'center';
            app.C1pFLabel_21.FontSize = 10;
            app.C1pFLabel_21.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_21.Layout.Row = 5;
            app.C1pFLabel_21.Layout.Column = 1;
            app.C1pFLabel_21.Interpreter = 'latex';
            app.C1pFLabel_21.Text = '电容值$C3(pF)$';

            % Create EditField_pi1_Set_C3_min
            app.EditField_pi1_Set_C3_min = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Set_C3_min.Limits = [0.01 Inf];
            app.EditField_pi1_Set_C3_min.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_C3_min.FontSize = 9;
            app.EditField_pi1_Set_C3_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_C3_min.Layout.Row = 5;
            app.EditField_pi1_Set_C3_min.Layout.Column = 2;
            app.EditField_pi1_Set_C3_min.Value = 0.01;

            % Create Label_16
            app.Label_16 = uilabel(app.GridLayout13_11);
            app.Label_16.HorizontalAlignment = 'center';
            app.Label_16.FontSize = 18;
            app.Label_16.FontWeight = 'bold';
            app.Label_16.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_16.Layout.Row = 5;
            app.Label_16.Layout.Column = 3;
            app.Label_16.Text = '~';

            % Create EditField_pi1_Set_C3_max
            app.EditField_pi1_Set_C3_max = uieditfield(app.GridLayout13_11, 'numeric');
            app.EditField_pi1_Set_C3_max.Limits = [0 Inf];
            app.EditField_pi1_Set_C3_max.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_C3_max.FontSize = 10;
            app.EditField_pi1_Set_C3_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_C3_max.Layout.Row = 5;
            app.EditField_pi1_Set_C3_max.Layout.Column = 4;

            % Create GridLayout13_12
            app.GridLayout13_12 = uigridlayout(app.GridLayout12_6);
            app.GridLayout13_12.ColumnWidth = {'2x', '1x', '1x', '1x'};
            app.GridLayout13_12.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_12.Layout.Row = 2;
            app.GridLayout13_12.Layout.Column = 2;
            app.GridLayout13_12.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_16
            app.LHLabel_16 = uilabel(app.GridLayout13_12);
            app.LHLabel_16.HorizontalAlignment = 'center';
            app.LHLabel_16.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_16.Layout.Row = 1;
            app.LHLabel_16.Layout.Column = 1;
            app.LHLabel_16.Interpreter = 'latex';
            app.LHLabel_16.Text = '选定电感值$L(μH)$';

            % Create EditField_pi1_Set_L_2
            app.EditField_pi1_Set_L_2 = uieditfield(app.GridLayout13_12, 'numeric');
            app.EditField_pi1_Set_L_2.Limits = [0 Inf];
            app.EditField_pi1_Set_L_2.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_L_2.FontSize = 10;
            app.EditField_pi1_Set_L_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_L_2.Layout.Row = 1;
            app.EditField_pi1_Set_L_2.Layout.Column = [2 4];

            % Create C1pFLabel_22
            app.C1pFLabel_22 = uilabel(app.GridLayout13_12);
            app.C1pFLabel_22.HorizontalAlignment = 'center';
            app.C1pFLabel_22.FontSize = 10;
            app.C1pFLabel_22.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_22.Layout.Row = 2;
            app.C1pFLabel_22.Layout.Column = 1;
            app.C1pFLabel_22.Interpreter = 'latex';
            app.C1pFLabel_22.Text = '目标负载阻抗 $Z_L$(单位Ω)';

            % Create EditField_pi1_Target_Z_Real
            app.EditField_pi1_Target_Z_Real = uieditfield(app.GridLayout13_12, 'numeric');
            app.EditField_pi1_Target_Z_Real.Limits = [0 Inf];
            app.EditField_pi1_Target_Z_Real.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Target_Z_Real.FontSize = 10;
            app.EditField_pi1_Target_Z_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Target_Z_Real.Layout.Row = 2;
            app.EditField_pi1_Target_Z_Real.Layout.Column = 2;
            app.EditField_pi1_Target_Z_Real.Value = 50;

            % Create Button_pi1_Backward
            app.Button_pi1_Backward = uibutton(app.GridLayout13_12, 'push');
            app.Button_pi1_Backward.ButtonPushedFcn = createCallbackFcn(app, @Button_pi1_BackwardPushed, true);
            app.Button_pi1_Backward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_pi1_Backward.FontSize = 18;
            app.Button_pi1_Backward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_pi1_Backward.Layout.Row = 4;
            app.Button_pi1_Backward.Layout.Column = [1 4];
            app.Button_pi1_Backward.Text = '反向计算所需电容值';

            % Create C1C2Label_4
            app.C1C2Label_4 = uilabel(app.GridLayout13_12);
            app.C1C2Label_4.HorizontalAlignment = 'center';
            app.C1C2Label_4.FontSize = 14;
            app.C1C2Label_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1C2Label_4.Layout.Row = 5;
            app.C1C2Label_4.Layout.Column = [1 4];
            app.C1C2Label_4.Interpreter = 'latex';
            app.C1C2Label_4.Text = '所需电容值：$C1、C2$';

            % Create Z_Load_minLabel_13
            app.Z_Load_minLabel_13 = uilabel(app.GridLayout13_12);
            app.Z_Load_minLabel_13.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_13.FontSize = 10;
            app.Z_Load_minLabel_13.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_13.Layout.Row = 6;
            app.Z_Load_minLabel_13.Layout.Column = 1;
            app.Z_Load_minLabel_13.Interpreter = 'latex';
            app.Z_Load_minLabel_13.Text = '所需电容值$C1(pF)=$';

            % Create EditField_pi1_Cal_C1
            app.EditField_pi1_Cal_C1 = uieditfield(app.GridLayout13_12, 'numeric');
            app.EditField_pi1_Cal_C1.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Cal_C1.Editable = 'off';
            app.EditField_pi1_Cal_C1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Cal_C1.Layout.Row = 6;
            app.EditField_pi1_Cal_C1.Layout.Column = [2 4];

            % Create Z_Load_maxLabel_12
            app.Z_Load_maxLabel_12 = uilabel(app.GridLayout13_12);
            app.Z_Load_maxLabel_12.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_12.FontSize = 10;
            app.Z_Load_maxLabel_12.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_12.Layout.Row = 7;
            app.Z_Load_maxLabel_12.Layout.Column = 1;
            app.Z_Load_maxLabel_12.Interpreter = 'latex';
            app.Z_Load_maxLabel_12.Text = '所需电容值$C2(pF)=$';

            % Create EditField_pi1_Cal_C2
            app.EditField_pi1_Cal_C2 = uieditfield(app.GridLayout13_12, 'numeric');
            app.EditField_pi1_Cal_C2.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Cal_C2.Editable = 'off';
            app.EditField_pi1_Cal_C2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Cal_C2.Layout.Row = 7;
            app.EditField_pi1_Cal_C2.Layout.Column = [2 4];

            % Create Button_Voltage_Max_pi1
            app.Button_Voltage_Max_pi1 = uibutton(app.GridLayout13_12, 'push');
            app.Button_Voltage_Max_pi1.ButtonPushedFcn = createCallbackFcn(app, @Button_Voltage_Max_Pushed, true);
            app.Button_Voltage_Max_pi1.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Voltage_Max_pi1.FontSize = 18;
            app.Button_Voltage_Max_pi1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Voltage_Max_pi1.Layout.Row = 8;
            app.Button_Voltage_Max_pi1.Layout.Column = [1 4];
            app.Button_Voltage_Max_pi1.Text = '反向计算的元件承压值';

            % Create jEditFieldLabel_6
            app.jEditFieldLabel_6 = uilabel(app.GridLayout13_12);
            app.jEditFieldLabel_6.HorizontalAlignment = 'center';
            app.jEditFieldLabel_6.FontName = 'Times New Roman';
            app.jEditFieldLabel_6.FontSize = 18;
            app.jEditFieldLabel_6.FontWeight = 'bold';
            app.jEditFieldLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jEditFieldLabel_6.Layout.Row = 2;
            app.jEditFieldLabel_6.Layout.Column = 3;
            app.jEditFieldLabel_6.Text = '+j';

            % Create EditField_pi1_Target_Z_Im
            app.EditField_pi1_Target_Z_Im = uieditfield(app.GridLayout13_12, 'numeric');
            app.EditField_pi1_Target_Z_Im.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Target_Z_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Target_Z_Im.Layout.Row = 2;
            app.EditField_pi1_Target_Z_Im.Layout.Column = 4;

            % Create Z_Load_minLabel_14
            app.Z_Load_minLabel_14 = uilabel(app.GridLayout13_12);
            app.Z_Load_minLabel_14.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_14.FontSize = 10;
            app.Z_Load_minLabel_14.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_14.Layout.Row = 3;
            app.Z_Load_minLabel_14.Layout.Column = 1;
            app.Z_Load_minLabel_14.Interpreter = 'latex';
            app.Z_Load_minLabel_14.Text = '选定电容值$C3(pF)=$';

            % Create EditField_pi1_Set_C3_2
            app.EditField_pi1_Set_C3_2 = uieditfield(app.GridLayout13_12, 'numeric');
            app.EditField_pi1_Set_C3_2.ValueDisplayFormat = '%.6f';
            app.EditField_pi1_Set_C3_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi1_Set_C3_2.Layout.Row = 3;
            app.EditField_pi1_Set_C3_2.Layout.Column = [2 4];

            % Create Tab_pi2_Home
            app.Tab_pi2_Home = uitab(app.TabGroup);
            app.Tab_pi2_Home.Title = 'pi 型电路 Ⅱ';
            app.Tab_pi2_Home.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_pi2_Home.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout5_7
            app.GridLayout5_7 = uigridlayout(app.Tab_pi2_Home);
            app.GridLayout5_7.ColumnWidth = {'1x'};
            app.GridLayout5_7.RowHeight = {'1x', '3x'};
            app.GridLayout5_7.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create GridLayout10_7
            app.GridLayout10_7 = uigridlayout(app.GridLayout5_7);
            app.GridLayout10_7.Layout.Row = 1;
            app.GridLayout10_7.Layout.Column = 1;
            app.GridLayout10_7.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create Image_pi2
            app.Image_pi2 = uiimage(app.GridLayout10_7);
            app.Image_pi2.Layout.Row = [1 2];
            app.Image_pi2.Layout.Column = 1;
            app.Image_pi2.ImageSource = fullfile(pathToMLAPP, 'Figure', 'pi2.png');

            % Create GridLayout11_7
            app.GridLayout11_7 = uigridlayout(app.GridLayout10_7);
            app.GridLayout11_7.Layout.Row = [1 2];
            app.GridLayout11_7.Layout.Column = 2;
            app.GridLayout11_7.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create fmathrmMHzLabel_5
            app.fmathrmMHzLabel_5 = uilabel(app.GridLayout11_7);
            app.fmathrmMHzLabel_5.HorizontalAlignment = 'center';
            app.fmathrmMHzLabel_5.FontSize = 18;
            app.fmathrmMHzLabel_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.fmathrmMHzLabel_5.Layout.Row = 1;
            app.fmathrmMHzLabel_5.Layout.Column = 1;
            app.fmathrmMHzLabel_5.Interpreter = 'latex';
            app.fmathrmMHzLabel_5.Text = '工作频率 $f$ / $\mathrm{MHz}$';

            % Create MHzLabel_8
            app.MHzLabel_8 = uilabel(app.GridLayout11_7);
            app.MHzLabel_8.HorizontalAlignment = 'center';
            app.MHzLabel_8.FontName = 'Times New Roman';
            app.MHzLabel_8.FontSize = 18;
            app.MHzLabel_8.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.MHzLabel_8.Layout.Row = 2;
            app.MHzLabel_8.Layout.Column = 2;
            app.MHzLabel_8.Interpreter = 'tex';
            app.MHzLabel_8.Text = '单位 MHz';

            % Create EditField_Operat_f_pi2
            app.EditField_Operat_f_pi2 = uieditfield(app.GridLayout11_7, 'numeric');
            app.EditField_Operat_f_pi2.Limits = [1 133];
            app.EditField_Operat_f_pi2.ValueDisplayFormat = '%.6f';
            app.EditField_Operat_f_pi2.FontSize = 18;
            app.EditField_Operat_f_pi2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Operat_f_pi2.Layout.Row = 2;
            app.EditField_Operat_f_pi2.Layout.Column = 1;
            app.EditField_Operat_f_pi2.Value = 1;

            % Create Button_Readme_pi2
            app.Button_Readme_pi2 = uibutton(app.GridLayout11_7, 'push');
            app.Button_Readme_pi2.ButtonPushedFcn = createCallbackFcn(app, @Button_Readme_pi2Pushed, true);
            app.Button_Readme_pi2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Readme_pi2.FontName = 'Times New Roman';
            app.Button_Readme_pi2.FontSize = 24;
            app.Button_Readme_pi2.FontWeight = 'bold';
            app.Button_Readme_pi2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Readme_pi2.Layout.Row = 1;
            app.Button_Readme_pi2.Layout.Column = 2;
            app.Button_Readme_pi2.Text = 'Read me';

            % Create GridLayout12_7
            app.GridLayout12_7 = uigridlayout(app.GridLayout5_7);
            app.GridLayout12_7.RowHeight = {'1x', '4x'};
            app.GridLayout12_7.Layout.Row = 2;
            app.GridLayout12_7.Layout.Column = 1;
            app.GridLayout12_7.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create textbfLC_1C_2C_3Z_mathrmloadLabel_5
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5 = uilabel(app.GridLayout12_7);
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.HorizontalAlignment = 'center';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.WordWrap = 'on';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.FontSize = 14;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.Layout.Row = 1;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.Layout.Column = 1;
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.Interpreter = 'latex';
            app.textbfLC_1C_2C_3Z_mathrmloadLabel_5.Text = '\textbf{正向计算}：设置元件参数 $(L, C_1, C_2, C_3)$，推导可匹配负载阻抗范围 $(Z_{\mathrm{load}})$';

            % Create textbfZ_mathrmLLC_3C_1C_2Label_3
            app.textbfZ_mathrmLLC_3C_1C_2Label_3 = uilabel(app.GridLayout12_7);
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.HorizontalAlignment = 'center';
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.WordWrap = 'on';
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.FontSize = 14;
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.Layout.Row = 1;
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.Layout.Column = 2;
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.Interpreter = 'latex';
            app.textbfZ_mathrmLLC_3C_1C_2Label_3.Text = '\textbf{反向计算}：目标负载阻抗 $Z_{\mathrm{L}}$ + 选定 $L$ + $C_3$，推导所需电容 $(C_1, C_2)$';

            % Create GridLayout13_13
            app.GridLayout13_13 = uigridlayout(app.GridLayout12_7);
            app.GridLayout13_13.ColumnWidth = {'1x', '1x', '1x', '1x'};
            app.GridLayout13_13.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_13.Layout.Row = 2;
            app.GridLayout13_13.Layout.Column = 1;
            app.GridLayout13_13.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_17
            app.LHLabel_17 = uilabel(app.GridLayout13_13);
            app.LHLabel_17.HorizontalAlignment = 'center';
            app.LHLabel_17.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_17.Layout.Row = 1;
            app.LHLabel_17.Layout.Column = 1;
            app.LHLabel_17.Interpreter = 'latex';
            app.LHLabel_17.Text = '电感值$L(μH)$';

            % Create EditField_pi2_Set_L
            app.EditField_pi2_Set_L = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Set_L.Limits = [0 Inf];
            app.EditField_pi2_Set_L.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_L.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_L.Layout.Row = 1;
            app.EditField_pi2_Set_L.Layout.Column = [2 4];

            % Create C1pFLabel_23
            app.C1pFLabel_23 = uilabel(app.GridLayout13_13);
            app.C1pFLabel_23.HorizontalAlignment = 'center';
            app.C1pFLabel_23.FontSize = 10;
            app.C1pFLabel_23.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_23.Layout.Row = 3;
            app.C1pFLabel_23.Layout.Column = 1;
            app.C1pFLabel_23.Interpreter = 'latex';
            app.C1pFLabel_23.Text = '电容值$C1(pF)$';

            % Create EditField_pi2_Set_C1_min
            app.EditField_pi2_Set_C1_min = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Set_C1_min.Limits = [0.01 Inf];
            app.EditField_pi2_Set_C1_min.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_C1_min.FontSize = 10;
            app.EditField_pi2_Set_C1_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_C1_min.Layout.Row = 3;
            app.EditField_pi2_Set_C1_min.Layout.Column = 2;
            app.EditField_pi2_Set_C1_min.Value = 0.01;

            % Create C1pFLabel_24
            app.C1pFLabel_24 = uilabel(app.GridLayout13_13);
            app.C1pFLabel_24.HorizontalAlignment = 'center';
            app.C1pFLabel_24.FontSize = 10;
            app.C1pFLabel_24.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_24.Layout.Row = 4;
            app.C1pFLabel_24.Layout.Column = 1;
            app.C1pFLabel_24.Interpreter = 'latex';
            app.C1pFLabel_24.Text = '电容值$C2(pF)$';

            % Create EditField_pi2_Set_C2_min
            app.EditField_pi2_Set_C2_min = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Set_C2_min.Limits = [0.01 Inf];
            app.EditField_pi2_Set_C2_min.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_C2_min.FontSize = 9;
            app.EditField_pi2_Set_C2_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_C2_min.Layout.Row = 4;
            app.EditField_pi2_Set_C2_min.Layout.Column = 2;
            app.EditField_pi2_Set_C2_min.Value = 0.01;

            % Create Button_pi2_Forward
            app.Button_pi2_Forward = uibutton(app.GridLayout13_13, 'push');
            app.Button_pi2_Forward.ButtonPushedFcn = createCallbackFcn(app, @Button_pi2_ForwardPushed, true);
            app.Button_pi2_Forward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_pi2_Forward.FontSize = 14;
            app.Button_pi2_Forward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_pi2_Forward.Layout.Row = 6;
            app.Button_pi2_Forward.Layout.Column = [1 4];
            app.Button_pi2_Forward.Text = '正向计算可匹配负载阻抗范围';

            % Create Z_LoadR_LjX_LLabel_7
            app.Z_LoadR_LjX_LLabel_7 = uilabel(app.GridLayout13_13);
            app.Z_LoadR_LjX_LLabel_7.HorizontalAlignment = 'center';
            app.Z_LoadR_LjX_LLabel_7.FontSize = 14;
            app.Z_LoadR_LjX_LLabel_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_LoadR_LjX_LLabel_7.Layout.Row = 7;
            app.Z_LoadR_LjX_LLabel_7.Layout.Column = [1 4];
            app.Z_LoadR_LjX_LLabel_7.Interpreter = 'latex';
            app.Z_LoadR_LjX_LLabel_7.Text = '可匹配负载阻抗范围：$Z_{Load} = R_L + jX_L$(单位Ω)';

            % Create Z_Load_minLabel_15
            app.Z_Load_minLabel_15 = uilabel(app.GridLayout13_13);
            app.Z_Load_minLabel_15.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_15.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_15.Layout.Row = 8;
            app.Z_Load_minLabel_15.Layout.Column = 1;
            app.Z_Load_minLabel_15.Interpreter = 'latex';
            app.Z_Load_minLabel_15.Text = '$Z_{Load_{min}} =$';

            % Create EditField_pi2_Cal_Zmin_Real
            app.EditField_pi2_Cal_Zmin_Real = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Cal_Zmin_Real.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Cal_Zmin_Real.Editable = 'off';
            app.EditField_pi2_Cal_Zmin_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Cal_Zmin_Real.Layout.Row = 8;
            app.EditField_pi2_Cal_Zmin_Real.Layout.Column = 2;

            % Create Z_Load_maxLabel_13
            app.Z_Load_maxLabel_13 = uilabel(app.GridLayout13_13);
            app.Z_Load_maxLabel_13.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_13.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_13.Layout.Row = 9;
            app.Z_Load_maxLabel_13.Layout.Column = 1;
            app.Z_Load_maxLabel_13.Interpreter = 'latex';
            app.Z_Load_maxLabel_13.Text = '$Z_{Load_{max}} =$';

            % Create EditField_pi2_Cal_Zmax_Real
            app.EditField_pi2_Cal_Zmax_Real = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Cal_Zmax_Real.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Cal_Zmax_Real.Editable = 'off';
            app.EditField_pi2_Cal_Zmax_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Cal_Zmax_Real.Layout.Row = 9;
            app.EditField_pi2_Cal_Zmax_Real.Layout.Column = 2;

            % Create EditField_pi2_Set_C1_max
            app.EditField_pi2_Set_C1_max = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Set_C1_max.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_C1_max.FontSize = 10;
            app.EditField_pi2_Set_C1_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_C1_max.Layout.Row = 3;
            app.EditField_pi2_Set_C1_max.Layout.Column = 4;

            % Create EditField_pi2_Set_C2_max
            app.EditField_pi2_Set_C2_max = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Set_C2_max.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_C2_max.FontSize = 10;
            app.EditField_pi2_Set_C2_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_C2_max.Layout.Row = 4;
            app.EditField_pi2_Set_C2_max.Layout.Column = 4;

            % Create minLabel_7
            app.minLabel_7 = uilabel(app.GridLayout13_13);
            app.minLabel_7.HorizontalAlignment = 'center';
            app.minLabel_7.FontName = 'Times New Roman';
            app.minLabel_7.FontSize = 18;
            app.minLabel_7.FontWeight = 'bold';
            app.minLabel_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.minLabel_7.Layout.Row = 2;
            app.minLabel_7.Layout.Column = 2;
            app.minLabel_7.Text = 'min';

            % Create maxLabel_7
            app.maxLabel_7 = uilabel(app.GridLayout13_13);
            app.maxLabel_7.HorizontalAlignment = 'center';
            app.maxLabel_7.FontName = 'Times New Roman';
            app.maxLabel_7.FontSize = 18;
            app.maxLabel_7.FontWeight = 'bold';
            app.maxLabel_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.maxLabel_7.Layout.Row = 2;
            app.maxLabel_7.Layout.Column = 4;
            app.maxLabel_7.Text = 'max';

            % Create EditField_pi2_Cal_Zmin_Im
            app.EditField_pi2_Cal_Zmin_Im = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Cal_Zmin_Im.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Cal_Zmin_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Cal_Zmin_Im.Layout.Row = 8;
            app.EditField_pi2_Cal_Zmin_Im.Layout.Column = 4;

            % Create EditField_pi2_Cal_Zmax_Im
            app.EditField_pi2_Cal_Zmax_Im = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Cal_Zmax_Im.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Cal_Zmax_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Cal_Zmax_Im.Layout.Row = 9;
            app.EditField_pi2_Cal_Zmax_Im.Layout.Column = 4;

            % Create Label_17
            app.Label_17 = uilabel(app.GridLayout13_13);
            app.Label_17.HorizontalAlignment = 'center';
            app.Label_17.FontSize = 18;
            app.Label_17.FontWeight = 'bold';
            app.Label_17.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_17.Layout.Row = 3;
            app.Label_17.Layout.Column = 3;
            app.Label_17.Text = '~';

            % Create Label_18
            app.Label_18 = uilabel(app.GridLayout13_13);
            app.Label_18.HorizontalAlignment = 'center';
            app.Label_18.FontSize = 18;
            app.Label_18.FontWeight = 'bold';
            app.Label_18.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_18.Layout.Row = 4;
            app.Label_18.Layout.Column = 3;
            app.Label_18.Text = '~';

            % Create jLabel_19
            app.jLabel_19 = uilabel(app.GridLayout13_13);
            app.jLabel_19.HorizontalAlignment = 'center';
            app.jLabel_19.FontName = 'Times New Roman';
            app.jLabel_19.FontSize = 18;
            app.jLabel_19.FontWeight = 'bold';
            app.jLabel_19.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_19.Layout.Row = 8;
            app.jLabel_19.Layout.Column = 3;
            app.jLabel_19.Text = '+j';

            % Create jLabel_20
            app.jLabel_20 = uilabel(app.GridLayout13_13);
            app.jLabel_20.HorizontalAlignment = 'center';
            app.jLabel_20.FontName = 'Times New Roman';
            app.jLabel_20.FontSize = 18;
            app.jLabel_20.FontWeight = 'bold';
            app.jLabel_20.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_20.Layout.Row = 9;
            app.jLabel_20.Layout.Column = 3;
            app.jLabel_20.Text = '+j';

            % Create C1pFLabel_25
            app.C1pFLabel_25 = uilabel(app.GridLayout13_13);
            app.C1pFLabel_25.HorizontalAlignment = 'center';
            app.C1pFLabel_25.FontSize = 10;
            app.C1pFLabel_25.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_25.Layout.Row = 5;
            app.C1pFLabel_25.Layout.Column = 1;
            app.C1pFLabel_25.Interpreter = 'latex';
            app.C1pFLabel_25.Text = '电容值$C3(pF)$';

            % Create EditField_pi2_Set_C3_min
            app.EditField_pi2_Set_C3_min = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Set_C3_min.Limits = [0.01 Inf];
            app.EditField_pi2_Set_C3_min.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_C3_min.FontSize = 9;
            app.EditField_pi2_Set_C3_min.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_C3_min.Layout.Row = 5;
            app.EditField_pi2_Set_C3_min.Layout.Column = 2;
            app.EditField_pi2_Set_C3_min.Value = 0.01;

            % Create Label_19
            app.Label_19 = uilabel(app.GridLayout13_13);
            app.Label_19.HorizontalAlignment = 'center';
            app.Label_19.FontSize = 18;
            app.Label_19.FontWeight = 'bold';
            app.Label_19.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_19.Layout.Row = 5;
            app.Label_19.Layout.Column = 3;
            app.Label_19.Text = '~';

            % Create EditField_pi2_Set_C3_max
            app.EditField_pi2_Set_C3_max = uieditfield(app.GridLayout13_13, 'numeric');
            app.EditField_pi2_Set_C3_max.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_C3_max.FontSize = 10;
            app.EditField_pi2_Set_C3_max.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_C3_max.Layout.Row = 5;
            app.EditField_pi2_Set_C3_max.Layout.Column = 4;

            % Create GridLayout13_14
            app.GridLayout13_14 = uigridlayout(app.GridLayout12_7);
            app.GridLayout13_14.ColumnWidth = {'2x', '1x', '1x', '1x'};
            app.GridLayout13_14.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout13_14.Layout.Row = 2;
            app.GridLayout13_14.Layout.Column = 2;
            app.GridLayout13_14.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create LHLabel_18
            app.LHLabel_18 = uilabel(app.GridLayout13_14);
            app.LHLabel_18.HorizontalAlignment = 'center';
            app.LHLabel_18.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.LHLabel_18.Layout.Row = 1;
            app.LHLabel_18.Layout.Column = 1;
            app.LHLabel_18.Interpreter = 'latex';
            app.LHLabel_18.Text = '选定电感值$L(μH)$';

            % Create EditField_pi2_Set_L_2
            app.EditField_pi2_Set_L_2 = uieditfield(app.GridLayout13_14, 'numeric');
            app.EditField_pi2_Set_L_2.Limits = [0 Inf];
            app.EditField_pi2_Set_L_2.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_L_2.FontSize = 10;
            app.EditField_pi2_Set_L_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_L_2.Layout.Row = 1;
            app.EditField_pi2_Set_L_2.Layout.Column = [2 4];

            % Create C1pFLabel_26
            app.C1pFLabel_26 = uilabel(app.GridLayout13_14);
            app.C1pFLabel_26.HorizontalAlignment = 'center';
            app.C1pFLabel_26.FontSize = 10;
            app.C1pFLabel_26.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1pFLabel_26.Layout.Row = 2;
            app.C1pFLabel_26.Layout.Column = 1;
            app.C1pFLabel_26.Interpreter = 'latex';
            app.C1pFLabel_26.Text = '目标负载阻抗 $Z_L$(单位Ω)';

            % Create EditField_pi2_Target_Z_Real
            app.EditField_pi2_Target_Z_Real = uieditfield(app.GridLayout13_14, 'numeric');
            app.EditField_pi2_Target_Z_Real.Limits = [0 Inf];
            app.EditField_pi2_Target_Z_Real.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Target_Z_Real.FontSize = 10;
            app.EditField_pi2_Target_Z_Real.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Target_Z_Real.Layout.Row = 2;
            app.EditField_pi2_Target_Z_Real.Layout.Column = 2;
            app.EditField_pi2_Target_Z_Real.Value = 50;

            % Create Button_pi2_Backward
            app.Button_pi2_Backward = uibutton(app.GridLayout13_14, 'push');
            app.Button_pi2_Backward.ButtonPushedFcn = createCallbackFcn(app, @Button_pi2_BackwardPushed, true);
            app.Button_pi2_Backward.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_pi2_Backward.FontSize = 18;
            app.Button_pi2_Backward.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_pi2_Backward.Layout.Row = 4;
            app.Button_pi2_Backward.Layout.Column = [1 4];
            app.Button_pi2_Backward.Text = '反向计算所需电容值';

            % Create C1C2Label_5
            app.C1C2Label_5 = uilabel(app.GridLayout13_14);
            app.C1C2Label_5.HorizontalAlignment = 'center';
            app.C1C2Label_5.FontSize = 14;
            app.C1C2Label_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.C1C2Label_5.Layout.Row = 5;
            app.C1C2Label_5.Layout.Column = [1 4];
            app.C1C2Label_5.Interpreter = 'latex';
            app.C1C2Label_5.Text = '所需电容值：$C1、C2$';

            % Create Z_Load_minLabel_16
            app.Z_Load_minLabel_16 = uilabel(app.GridLayout13_14);
            app.Z_Load_minLabel_16.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_16.FontSize = 10;
            app.Z_Load_minLabel_16.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_16.Layout.Row = 6;
            app.Z_Load_minLabel_16.Layout.Column = 1;
            app.Z_Load_minLabel_16.Interpreter = 'latex';
            app.Z_Load_minLabel_16.Text = '所需电容值$C1(pF)=$';

            % Create EditField_pi2_Cal_C1
            app.EditField_pi2_Cal_C1 = uieditfield(app.GridLayout13_14, 'numeric');
            app.EditField_pi2_Cal_C1.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Cal_C1.Editable = 'off';
            app.EditField_pi2_Cal_C1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Cal_C1.Layout.Row = 6;
            app.EditField_pi2_Cal_C1.Layout.Column = [2 4];

            % Create Z_Load_maxLabel_14
            app.Z_Load_maxLabel_14 = uilabel(app.GridLayout13_14);
            app.Z_Load_maxLabel_14.HorizontalAlignment = 'center';
            app.Z_Load_maxLabel_14.FontSize = 10;
            app.Z_Load_maxLabel_14.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_maxLabel_14.Layout.Row = 7;
            app.Z_Load_maxLabel_14.Layout.Column = 1;
            app.Z_Load_maxLabel_14.Interpreter = 'latex';
            app.Z_Load_maxLabel_14.Text = '所需电容值$C2(pF)=$';

            % Create EditField_pi2_Cal_C2
            app.EditField_pi2_Cal_C2 = uieditfield(app.GridLayout13_14, 'numeric');
            app.EditField_pi2_Cal_C2.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Cal_C2.Editable = 'off';
            app.EditField_pi2_Cal_C2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Cal_C2.Layout.Row = 7;
            app.EditField_pi2_Cal_C2.Layout.Column = [2 4];

            % Create Button_Voltage_Max_pi2
            app.Button_Voltage_Max_pi2 = uibutton(app.GridLayout13_14, 'push');
            app.Button_Voltage_Max_pi2.ButtonPushedFcn = createCallbackFcn(app, @Button_Voltage_Max_Pushed, true);
            app.Button_Voltage_Max_pi2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Voltage_Max_pi2.FontSize = 18;
            app.Button_Voltage_Max_pi2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Voltage_Max_pi2.Layout.Row = 8;
            app.Button_Voltage_Max_pi2.Layout.Column = [1 4];
            app.Button_Voltage_Max_pi2.Text = '反向计算的元件承压值';

            % Create jEditFieldLabel_7
            app.jEditFieldLabel_7 = uilabel(app.GridLayout13_14);
            app.jEditFieldLabel_7.HorizontalAlignment = 'center';
            app.jEditFieldLabel_7.FontName = 'Times New Roman';
            app.jEditFieldLabel_7.FontSize = 18;
            app.jEditFieldLabel_7.FontWeight = 'bold';
            app.jEditFieldLabel_7.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jEditFieldLabel_7.Layout.Row = 2;
            app.jEditFieldLabel_7.Layout.Column = 3;
            app.jEditFieldLabel_7.Text = '+j';

            % Create EditField_pi2_Target_Z_Im
            app.EditField_pi2_Target_Z_Im = uieditfield(app.GridLayout13_14, 'numeric');
            app.EditField_pi2_Target_Z_Im.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Target_Z_Im.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Target_Z_Im.Layout.Row = 2;
            app.EditField_pi2_Target_Z_Im.Layout.Column = 4;

            % Create Z_Load_minLabel_17
            app.Z_Load_minLabel_17 = uilabel(app.GridLayout13_14);
            app.Z_Load_minLabel_17.HorizontalAlignment = 'center';
            app.Z_Load_minLabel_17.FontSize = 10;
            app.Z_Load_minLabel_17.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Z_Load_minLabel_17.Layout.Row = 3;
            app.Z_Load_minLabel_17.Layout.Column = 1;
            app.Z_Load_minLabel_17.Interpreter = 'latex';
            app.Z_Load_minLabel_17.Text = '选定电容值$C3(pF)=$';

            % Create EditField_pi2_Set_C3
            app.EditField_pi2_Set_C3 = uieditfield(app.GridLayout13_14, 'numeric');
            app.EditField_pi2_Set_C3.ValueDisplayFormat = '%.6f';
            app.EditField_pi2_Set_C3.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_pi2_Set_C3.Layout.Row = 3;
            app.EditField_pi2_Set_C3.Layout.Column = [2 4];

            % Create Tab_Z2Y_Home
            app.Tab_Z2Y_Home = uitab(app.TabGroup);
            app.Tab_Z2Y_Home.Title = '阻抗导纳计算';
            app.Tab_Z2Y_Home.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_Z2Y_Home.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout2_2
            app.GridLayout2_2 = uigridlayout(app.Tab_Z2Y_Home);
            app.GridLayout2_2.RowHeight = {'1x', '1x', '1x', '1x', '1x', '1x'};
            app.GridLayout2_2.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create GridLayout3_3
            app.GridLayout3_3 = uigridlayout(app.GridLayout2_2);
            app.GridLayout3_3.ColumnWidth = {'1x', '4x', '1x', '4x'};
            app.GridLayout3_3.RowHeight = {'1x'};
            app.GridLayout3_3.Layout.Row = 3;
            app.GridLayout3_3.Layout.Column = 1;
            app.GridLayout3_3.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create jLabel
            app.jLabel = uilabel(app.GridLayout3_3);
            app.jLabel.HorizontalAlignment = 'center';
            app.jLabel.FontName = 'Times New Roman';
            app.jLabel.FontSize = 24;
            app.jLabel.FontWeight = 'bold';
            app.jLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel.Layout.Row = 1;
            app.jLabel.Layout.Column = 3;
            app.jLabel.Text = '+j';

            % Create EditField_Z_R
            app.EditField_Z_R = uieditfield(app.GridLayout3_3, 'numeric');
            app.EditField_Z_R.ValueDisplayFormat = '%.6f';
            app.EditField_Z_R.FontSize = 18;
            app.EditField_Z_R.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Z_R.Layout.Row = 1;
            app.EditField_Z_R.Layout.Column = 2;

            % Create EditField_Z_X
            app.EditField_Z_X = uieditfield(app.GridLayout3_3, 'numeric');
            app.EditField_Z_X.ValueDisplayFormat = '%.6f';
            app.EditField_Z_X.FontSize = 18;
            app.EditField_Z_X.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Z_X.Layout.Row = 1;
            app.EditField_Z_X.Layout.Column = 4;

            % Create ZLabel
            app.ZLabel = uilabel(app.GridLayout3_3);
            app.ZLabel.FontSize = 24;
            app.ZLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.ZLabel.Layout.Row = 1;
            app.ZLabel.Layout.Column = 1;
            app.ZLabel.Text = 'Z=';

            % Create Button_z2y
            app.Button_z2y = uibutton(app.GridLayout2_2, 'push');
            app.Button_z2y.ButtonPushedFcn = createCallbackFcn(app, @Button_z2yPushed, true);
            app.Button_z2y.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_z2y.FontSize = 36;
            app.Button_z2y.FontWeight = 'bold';
            app.Button_z2y.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_z2y.Layout.Row = 4;
            app.Button_z2y.Layout.Column = 1;
            app.Button_z2y.Text = '计算导纳';

            % Create itY1itZLabel
            app.itY1itZLabel = uilabel(app.GridLayout2_2);
            app.itY1itZLabel.HorizontalAlignment = 'center';
            app.itY1itZLabel.WordWrap = 'on';
            app.itY1itZLabel.FontSize = 18;
            app.itY1itZLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.itY1itZLabel.Layout.Row = 1;
            app.itY1itZLabel.Layout.Column = 1;
            app.itY1itZLabel.Interpreter = 'tex';
            app.itY1itZLabel.Text = {'阻抗换算导纳 '; '基本关系：'; '{\itY} = 1 / {\itZ}'};

            % Create itZ1itYLabel
            app.itZ1itYLabel = uilabel(app.GridLayout2_2);
            app.itZ1itYLabel.HorizontalAlignment = 'center';
            app.itZ1itYLabel.FontSize = 18;
            app.itZ1itYLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.itZ1itYLabel.Layout.Row = 1;
            app.itZ1itYLabel.Layout.Column = 2;
            app.itZ1itYLabel.Interpreter = 'tex';
            app.itZ1itYLabel.Text = {'导纳换算阻抗'; '基本关系：'; '{\itZ} = 1 / {\itY}'};

            % Create Button_y2z
            app.Button_y2z = uibutton(app.GridLayout2_2, 'push');
            app.Button_y2z.ButtonPushedFcn = createCallbackFcn(app, @Button_y2zPushed, true);
            app.Button_y2z.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_y2z.FontSize = 36;
            app.Button_y2z.FontWeight = 'bold';
            app.Button_y2z.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_y2z.Layout.Row = 4;
            app.Button_y2z.Layout.Column = 2;
            app.Button_y2z.Text = '计算阻抗';

            % Create itZitRjitXitRitXLabel
            app.itZitRjitXitRitXLabel = uilabel(app.GridLayout2_2);
            app.itZitRjitXitRitXLabel.HorizontalAlignment = 'center';
            app.itZitRjitXitRitXLabel.FontSize = 18;
            app.itZitRjitXitRitXLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.itZitRjitXitRitXLabel.Layout.Row = 2;
            app.itZitRjitXitRitXLabel.Layout.Column = 1;
            app.itZitRjitXitRitXLabel.Interpreter = 'tex';
            app.itZitRjitXitRitXLabel.Text = {'设阻抗 {\itZ} = {\itR} + j{\itX}'; '(其中 {\itR} 为电阻，{\itX} 为电抗)'};

            % Create itYitGjitBitGitBLabel
            app.itYitGjitBitGitBLabel = uilabel(app.GridLayout2_2);
            app.itYitGjitBitGitBLabel.HorizontalAlignment = 'center';
            app.itYitGjitBitGitBLabel.FontSize = 18;
            app.itYitGjitBitGitBLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.itYitGjitBitGitBLabel.Layout.Row = 2;
            app.itYitGjitBitGitBLabel.Layout.Column = 2;
            app.itYitGjitBitGitBLabel.Interpreter = 'tex';
            app.itYitGjitBitGitBLabel.Text = {'设导纳 {\itY} = {\itG} + j{\itB}'; '(其中 {\itG} 为电导，{\itB} 为电纳)'};

            % Create itGitRitR2itX2itBitXitR2itX2Label
            app.itGitRitR2itX2itBitXitR2itX2Label = uilabel(app.GridLayout2_2);
            app.itGitRitR2itX2itBitXitR2itX2Label.HorizontalAlignment = 'center';
            app.itGitRitR2itX2itBitXitR2itX2Label.WordWrap = 'on';
            app.itGitRitR2itX2itBitXitR2itX2Label.FontSize = 18;
            app.itGitRitR2itX2itBitXitR2itX2Label.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.itGitRitR2itX2itBitXitR2itX2Label.Layout.Row = 5;
            app.itGitRitR2itX2itBitXitR2itX2Label.Layout.Column = 1;
            app.itGitRitR2itX2itBitXitR2itX2Label.Interpreter = 'tex';
            app.itGitRitR2itX2itBitXitR2itX2Label.Text = {'转换公式如下：'; '{\itG} = {\itR} / ({\itR}^2 + {\itX}^2)'; '{\itB} = -{\itX} / ({\itR}^2 + {\itX}^2)'};

            % Create GridLayout3_5
            app.GridLayout3_5 = uigridlayout(app.GridLayout2_2);
            app.GridLayout3_5.ColumnWidth = {'1x', '4x', '1x', '4x'};
            app.GridLayout3_5.RowHeight = {'1x'};
            app.GridLayout3_5.Layout.Row = 3;
            app.GridLayout3_5.Layout.Column = 2;
            app.GridLayout3_5.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create jLabel_2
            app.jLabel_2 = uilabel(app.GridLayout3_5);
            app.jLabel_2.HorizontalAlignment = 'center';
            app.jLabel_2.FontName = 'Times New Roman';
            app.jLabel_2.FontSize = 24;
            app.jLabel_2.FontWeight = 'bold';
            app.jLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_2.Layout.Row = 1;
            app.jLabel_2.Layout.Column = 3;
            app.jLabel_2.Text = '+j';

            % Create EditField_Y_G
            app.EditField_Y_G = uieditfield(app.GridLayout3_5, 'numeric');
            app.EditField_Y_G.ValueDisplayFormat = '%.6f';
            app.EditField_Y_G.FontSize = 18;
            app.EditField_Y_G.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Y_G.Layout.Row = 1;
            app.EditField_Y_G.Layout.Column = 2;

            % Create EditField_Y_B
            app.EditField_Y_B = uieditfield(app.GridLayout3_5, 'numeric');
            app.EditField_Y_B.ValueDisplayFormat = '%.6f';
            app.EditField_Y_B.FontSize = 18;
            app.EditField_Y_B.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Y_B.Layout.Row = 1;
            app.EditField_Y_B.Layout.Column = 4;

            % Create YLabel
            app.YLabel = uilabel(app.GridLayout3_5);
            app.YLabel.FontSize = 24;
            app.YLabel.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.YLabel.Layout.Row = 1;
            app.YLabel.Layout.Column = 1;
            app.YLabel.Text = 'Y=';

            % Create GridLayout3_7
            app.GridLayout3_7 = uigridlayout(app.GridLayout2_2);
            app.GridLayout3_7.ColumnWidth = {'1x', '4x', '1x', '4x'};
            app.GridLayout3_7.RowHeight = {'1x'};
            app.GridLayout3_7.Layout.Row = 6;
            app.GridLayout3_7.Layout.Column = 1;
            app.GridLayout3_7.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create jLabel_4
            app.jLabel_4 = uilabel(app.GridLayout3_7);
            app.jLabel_4.HorizontalAlignment = 'center';
            app.jLabel_4.FontName = 'Times New Roman';
            app.jLabel_4.FontSize = 24;
            app.jLabel_4.FontWeight = 'bold';
            app.jLabel_4.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_4.Layout.Row = 1;
            app.jLabel_4.Layout.Column = 3;
            app.jLabel_4.Text = '+j';

            % Create EditField_Y_G_output
            app.EditField_Y_G_output = uieditfield(app.GridLayout3_7, 'numeric');
            app.EditField_Y_G_output.ValueDisplayFormat = '%.6f';
            app.EditField_Y_G_output.Editable = 'off';
            app.EditField_Y_G_output.FontSize = 18;
            app.EditField_Y_G_output.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Y_G_output.Layout.Row = 1;
            app.EditField_Y_G_output.Layout.Column = 2;

            % Create EditField_Y_B_output
            app.EditField_Y_B_output = uieditfield(app.GridLayout3_7, 'numeric');
            app.EditField_Y_B_output.ValueDisplayFormat = '%.6f';
            app.EditField_Y_B_output.Editable = 'off';
            app.EditField_Y_B_output.FontSize = 18;
            app.EditField_Y_B_output.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Y_B_output.Layout.Row = 1;
            app.EditField_Y_B_output.Layout.Column = 4;

            % Create YLabel_2
            app.YLabel_2 = uilabel(app.GridLayout3_7);
            app.YLabel_2.FontSize = 24;
            app.YLabel_2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.YLabel_2.Layout.Row = 1;
            app.YLabel_2.Layout.Column = 1;
            app.YLabel_2.Text = 'Y=';

            % Create GridLayout3_9
            app.GridLayout3_9 = uigridlayout(app.GridLayout2_2);
            app.GridLayout3_9.ColumnWidth = {'1x', '4x', '1x', '4x'};
            app.GridLayout3_9.RowHeight = {'1x'};
            app.GridLayout3_9.Layout.Row = 6;
            app.GridLayout3_9.Layout.Column = 2;
            app.GridLayout3_9.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create jLabel_6
            app.jLabel_6 = uilabel(app.GridLayout3_9);
            app.jLabel_6.HorizontalAlignment = 'center';
            app.jLabel_6.FontName = 'Times New Roman';
            app.jLabel_6.FontSize = 24;
            app.jLabel_6.FontWeight = 'bold';
            app.jLabel_6.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.jLabel_6.Layout.Row = 1;
            app.jLabel_6.Layout.Column = 3;
            app.jLabel_6.Text = '+j';

            % Create EditField_Z_R_output
            app.EditField_Z_R_output = uieditfield(app.GridLayout3_9, 'numeric');
            app.EditField_Z_R_output.ValueDisplayFormat = '%.6f';
            app.EditField_Z_R_output.Editable = 'off';
            app.EditField_Z_R_output.FontSize = 18;
            app.EditField_Z_R_output.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Z_R_output.Layout.Row = 1;
            app.EditField_Z_R_output.Layout.Column = 2;

            % Create EditField_Z_X_output
            app.EditField_Z_X_output = uieditfield(app.GridLayout3_9, 'numeric');
            app.EditField_Z_X_output.ValueDisplayFormat = '%.6f';
            app.EditField_Z_X_output.Editable = 'off';
            app.EditField_Z_X_output.FontSize = 18;
            app.EditField_Z_X_output.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.EditField_Z_X_output.Layout.Row = 1;
            app.EditField_Z_X_output.Layout.Column = 4;

            % Create ZLabel_5
            app.ZLabel_5 = uilabel(app.GridLayout3_9);
            app.ZLabel_5.FontSize = 24;
            app.ZLabel_5.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.ZLabel_5.Layout.Row = 1;
            app.ZLabel_5.Layout.Column = 1;
            app.ZLabel_5.Text = 'Z=';

            % Create itRitGitG2itB2itXitBitG2itB2Label
            app.itRitGitG2itB2itXitBitG2itB2Label = uilabel(app.GridLayout2_2);
            app.itRitGitG2itB2itXitBitG2itB2Label.HorizontalAlignment = 'center';
            app.itRitGitG2itB2itXitBitG2itB2Label.FontSize = 18;
            app.itRitGitG2itB2itXitBitG2itB2Label.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.itRitGitG2itB2itXitBitG2itB2Label.Layout.Row = 5;
            app.itRitGitG2itB2itXitBitG2itB2Label.Layout.Column = 2;
            app.itRitGitG2itB2itXitBitG2itB2Label.Interpreter = 'tex';
            app.itRitGitG2itB2itXitBitG2itB2Label.Text = {'转换公式如下：'; '{\itR} = {\itG} / ({\itG}^2 + {\itB}^2)'; '{\itX} = -{\itB} / ({\itG}^2 + {\itB}^2)'};

            % Create Tab_About_Home
            app.Tab_About_Home = uitab(app.TabGroup);
            app.Tab_About_Home.Title = 'About';
            app.Tab_About_Home.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Tab_About_Home.ForegroundColor = [0.129411764705882 0.129411764705882 0.129411764705882];

            % Create GridLayout_About
            app.GridLayout_About = uigridlayout(app.Tab_About_Home);
            app.GridLayout_About.ColumnWidth = {'1x'};
            app.GridLayout_About.RowHeight = {'1x', '1x', '3x', '1x'};
            app.GridLayout_About.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];

            % Create Label_About
            app.Label_About = uilabel(app.GridLayout_About);
            app.Label_About.HorizontalAlignment = 'center';
            app.Label_About.FontName = 'Times New Roman';
            app.Label_About.FontSize = 48;
            app.Label_About.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Label_About.Layout.Row = 1;
            app.Label_About.Layout.Column = 1;
            app.Label_About.Text = 'About';

            % Create Introduction1
            app.Introduction1 = uilabel(app.GridLayout_About);
            app.Introduction1.HorizontalAlignment = 'center';
            app.Introduction1.FontName = '宋体';
            app.Introduction1.FontSize = 24;
            app.Introduction1.FontWeight = 'bold';
            app.Introduction1.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Introduction1.Layout.Row = 2;
            app.Introduction1.Layout.Column = 1;
            app.Introduction1.Text = '******欢迎使用阻抗匹配辅助设计程序******';

            % Create Introduction2
            app.Introduction2 = uilabel(app.GridLayout_About);
            app.Introduction2.WordWrap = 'on';
            app.Introduction2.FontName = '宋体';
            app.Introduction2.FontSize = 14;
            app.Introduction2.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Introduction2.Layout.Row = 3;
            app.Introduction2.Layout.Column = 1;
            app.Introduction2.Interpreter = 'tex';
            app.Introduction2.Text = {'  本程序提供L型和 \pi 型（本设计中称为 \pi I 型）两种常用的集总参数匹配网络结构以及经L型电路经改造得到的的 \pi II 型电路供选择，可以根据使用者设定的频率、元件参数计算出可调节匹配的负载阻抗（或导纳）范围（包括实部、虚部）；也可以根据使用者设定的负载阻抗和若干固定元件值给出匹配网络其他参数。注意所有结果都是以匹配到50欧姆为准。'; ''; '  本程序还加入了一个阻抗导纳互换模块，可方便地进行阻抗与导纳之间的换算。'};

            % Create SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label = uilabel(app.GridLayout_About);
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label.HorizontalAlignment = 'center';
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label.FontName = 'Times New Roman';
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label.FontSize = 14;
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label.Layout.Row = 4;
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label.Layout.Column = 1;
            app.SJTURuilinLuKejiLuZhiyiLinYunleiZhangAllRightsReserved2025Label.Text = {'SJTU Ruilin Lu, Keji Lu,Zhiyi Lin,Yunlei Zhang. All Rights Reserved，2025.'; '523031910566'};

            % Create Button_SmithPlot
            app.Button_SmithPlot = uibutton(app.RightPanel, 'push');
            app.Button_SmithPlot.ButtonPushedFcn = createCallbackFcn(app, @Button_SmithPlotPushed, true);
            app.Button_SmithPlot.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_SmithPlot.FontName = 'Times New Roman';
            app.Button_SmithPlot.FontSize = 14;
            app.Button_SmithPlot.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_SmithPlot.Position = [679 7 104 25];
            app.Button_SmithPlot.Text = 'Smith圆图表示';

            % Create Button_Back
            app.Button_Back = uibutton(app.RightPanel, 'push');
            app.Button_Back.ButtonPushedFcn = createCallbackFcn(app, @Button_BackPushed, true);
            app.Button_Back.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Back.FontName = 'Times New Roman';
            app.Button_Back.FontSize = 14;
            app.Button_Back.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Back.Position = [14 6 100 25];
            app.Button_Back.Text = 'Back';

            % Create Button_Next
            app.Button_Next = uibutton(app.RightPanel, 'push');
            app.Button_Next.ButtonPushedFcn = createCallbackFcn(app, @Button_NextPushed, true);
            app.Button_Next.BackgroundColor = [0.96078431372549 0.96078431372549 0.96078431372549];
            app.Button_Next.FontName = 'Times New Roman';
            app.Button_Next.FontSize = 14;
            app.Button_Next.FontColor = [0.129411764705882 0.129411764705882 0.129411764705882];
            app.Button_Next.Position = [348 7 100 25];
            app.Button_Next.Text = 'Next';

            % Show the figure after all components are created
            app.UIFigure.Visible = 'on';
        end
    end

    % App creation and deletion
    methods (Access = public)

        % Construct app
        function app = MW_V1

            % Create UIFigure and components
            createComponents(app)

            % Register the app with App Designer
            registerApp(app, app.UIFigure)

            % Execute the startup function
            runStartupFcn(app, @startupFcn)

            if nargout == 0
                clear app
            end
        end

        % Code that executes before app deletion
        function delete(app)

            % Delete UIFigure when app is deleted
            delete(app.UIFigure)
        end
    end
end