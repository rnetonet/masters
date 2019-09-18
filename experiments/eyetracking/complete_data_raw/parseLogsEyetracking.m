function [xData,yData,pupData,info] = parseLogsEyetracking( logDir,viewFig,saveFig )
%PARSELOGSEYETRACKING extract eyetracking data from the analog data files
%
%
%   INPUT
%    ------------------------------------------------------------------------------------
%      logDir                - filepath to the log files (ex: {'ded00800'}
%      options               - 'loadfromMat' to load from the mat files
%                              instead of parsing the raw files again
%                              'saveMat' to store the result in .mat files
%
%    OUTPUT
%    ------------------------------------------------------------------------------------
%
%      xData                    - 2D array containing the X coordinates (dim info.nbTrials x info.durTrials)
%      xData                    - 2D array containing the Y coordinates (dim info.nbTrials x info.durTrials)
%      pupData                  - 2D array containing the Pupil Size values (dim info.nbTrials x info.durTrials)
%
%      info.nbTrials            - number of trials
%      info.durTrials           - duration of trials
%      info.freq                - frequency of acquisition
%      info.stim                - array containing the stimuli presented for each trial
%
%
%   Author:      Adrien Brilhault
%   Date:        2017-06-15
%   E-mail:      adrien.brilhault@gmail.com
%


xData=[];
yData=[];
pupData=[];
info=[];
info.nbTrials=[];
info.durTrials=[];
info.nbAnalogChanels=[];
info.freq=1000; % Default value = 1000hz


%% Params
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if ~exist('viewFig','var')
    viewFig='false';
end
if ~exist('saveFig','var')
    saveFig='false';
end
if ~exist('logDir','var')
    logDir='ded00800';
end

%logDir='ded00800';
%logDir='ded014a04';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Parse Experiment Infos
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Read the files in folder
fprintf('\n############# Loading files from %s\n\n',logDir);
if  ~isdir(logDir)
    fprintf('\nERROR: FOLDER "%s" DOES NOT EXIST!!!\n\n',logDir);
    return;
end

listFiles = dir([logDir,'/*.txt']);
if isempty(listFiles)
    fprintf('\nERROR: NO TEXT FILES IN "%s"!!!\n\n',logDir);
    return;
end
listFiles={listFiles(:).name};

%% Open info file in read-only mode
filename=[logDir '/' listFiles{cellfun(@(x) ~isempty(x),strfind(listFiles,'info'))} ];
file = fopen(filename,'r');
if file==-1
    fprintf('\nERROR: COULD NOT OPEN INFO FILE!!!\n\n');
    return;
else
    fprintf('# Parsing %s\n',filename);
end

tline = fgets(file);
while ischar(tline)
    
    %% skip blank lines
    if length(tline)==1
        tline = fgets(file);
        continue
    end
    
    if strfind(tline,'trials')
        info.nbTrials=str2num(tline(findstr(tline,':')+1:end));
    end
    
    if strfind(tline,'length')
        info.durTrials =str2num(tline(findstr(tline,':')+1:end));
    end
    
    if strfind(tline,'N of analog channels')
        info.nbAnalogChanels=str2num(tline(findstr(tline,':')+1:end));
    end
    
    tline = fgetl(file);
end
fclose(file);

%Display info values
info

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Parse Analog Data File
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% Open info file in read-only mode
filename=[logDir '/' listFiles{cellfun(@(x) ~isempty(x),strfind(listFiles,'analog'))} ];
file = fopen(filename,'r');
if file==-1
    fprintf('\nERROR: COULD NOT OPEN ANALOG FILE !!!\n\n');
    return;
else
    fprintf('# Parsing %s\n',filename);
end

% The file should have info.durTrials coluns (one for each time sample)
tline = fgets(file);
tmpData = textscan(tline,'%d');
nbCols = size(tmpData{1},1);
if nbCols~=info.durTrials
    fprintf('\nWARNING: THERE ARE %d COLUNS INSTEAD OF %d!!!\n\n', nbCols,info.durTrials);
end
frewind(file);

%% Read data
data = cell2mat(textscan(file,repmat('\t%d',1,nbCols)));
fclose(file);

% The file should have info.nbAnalogChanels*info.nbTrials lines
if size(data,1)~=info.nbAnalogChanels*info.nbTrials
    fprintf('\nWARNING: THERE ARE %d COLUNS INSTEAD OF %d!!!\n\n', size(data,1), info.nbAnalogChanels*info.nbTrials);
end;

% Return values (WARNING, it used to be X, Y, Pup - now it's Pup, X, Y)
xData=data(mod(1:size(data,1),info.nbAnalogChanels)==info.nbAnalogChanels-2,:);
yData=data(mod(1:size(data,1),info.nbAnalogChanels)==info.nbAnalogChanels-1,:);
pupData=data(mod(1:size(data,1),info.nbAnalogChanels)==0,:);

% xData=data(mod(1:size(data,1),info.nbAnalogChanels)==info.nbAnalogChanels-1,:);
% yData=data(mod(1:size(data,1),info.nbAnalogChanels)==0,:);
% pupData=data(mod(1:size(data,1),info.nbAnalogChanels)==info.nbAnalogChanels-2,:);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Parse Stim File
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Open info file in read-only mode
filename=[logDir '/' listFiles{cellfun(@(x) ~isempty(x),strfind(listFiles,'stim'))} ];
file = fopen(filename,'r');
if file==-1
    fprintf('\nWARNING: COULD NOT OPEN STIM FILE!!!\n\n');
    info.stim = repmat([1],1,info.nbTrials);


else
    fprintf('# Parsing %s\n',filename);
    %% Read data
    data = cell2mat(textscan(file,'%d'));
    fclose(file);
    
    % The file should have info.nbAnalogChanels*info.nbTrials lines
    if size(data,1)~=info.nbTrials
        fprintf('\nWARNING: THERE ARE %d COLUNS INSTEAD OF %d!!!\n\n', size(data,1), info.nbAnalogChanels*info.nbTrials);
    end;
    
    info.stim = data';
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Parse Behave File
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Open info file in read-only mode
filename=[logDir '/' listFiles{cellfun(@(x) ~isempty(x),strfind(listFiles,'behave'))} ];
file = fopen(filename,'r');
if file==-1
    fprintf('\nWARNING: COULD NOT OPEN BEHAVE FILE!!!\n\n');
    info.failed = repmat([0],1,info.nbTrials);
else
    fprintf('# Parsing %s\n',filename);
    
    % Read data
    data = cell2mat(textscan(file,'%d'));
    fclose(file);
    
    % The file should have info.nbAnalogChanels*info.nbTrials lines
    if size(data,1)~=info.nbTrials
        fprintf('\nWARNING: THERE ARE %d COLUNS INSTEAD OF %d!!!\n\n', size(data,1), info.nbAnalogChanels*info.nbTrials);
    end;
    
    info.failed = data'==0;
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Plot figures
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% plot all points
if false
    figure
    hold on
    plot(reshape(xData',1,[]),reshape(yData',1,[]),'k.','MarkerSize',5,'LineWidth',1);
    axis([-35000 35000 -35000 35000]);
    axis square
    hold off
end

%hist(reshape(double('xData'),1,[]));

%% Plot figure with points in different color for each condition
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



for dur=[1 500; 1000 min(1500,info.durTrials); 1 info.durTrials]'
    
    f=figure('visible','on');
    hold on
    
    %% Plot Data
    stims=unique(info.stim);
    for i=1:length(stims)
        plot(reshape(xData(info.stim==stims(i),dur(1):dur(2))',1,[]),reshape(yData(info.stim==stims(i),dur(1):dur(2))',1,[]),...
            '.','MarkerSize',1,'LineWidth',1,'color',subindex(hsv(length(stims)+1),i));
    end
    set(f,'Position',[1 10 1000 900]);
    axis equal
    axis([-35000 35000 -35000 35000]);
    
    %% Display the title & axes
    xlabel('Xpos (Analog values)');
    ylabel('Ypos (Analog values)');
    titleFig=['Eyetracking positions in ' logDir ' (duration ' num2str(dur','%g-%g') ' ms)'] ;
    t=title(titleFig);
    set(t,'Interpreter','none');
    
    %% SaveFig
    hold off
    if saveFig
        filename=strrep(titleFig,'data/','');
        %filename(isspace(filename)) = []; %removing blank characters
        %filename(filename==10) = []; %removing new line characters
        folderFigures='figures';
        if ~exist(folderFigures,'dir')
            mkdir(folderFigures);
        end
        saveas(f,[folderFigures filesep filename '.fig']);
        saveas(f,[folderFigures filesep filename '.png']);
        saveas(f,[folderFigures filesep filename '.pdf']);

    end
    
     if ~viewFig
         close
     end
end
% fclose('all');clear;close all; pack;

