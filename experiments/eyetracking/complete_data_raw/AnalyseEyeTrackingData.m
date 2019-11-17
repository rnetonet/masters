% analyseEyeTrackingData - detect saccades and fixation
%
%
%   Author:      Adrien Brilhault
%   Date:        2017-06-15
%   E-mail:      adrien.brilhault@gmail.com
%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Buffalolab (based on unsupervised K-Means)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear;

%% Parameters
freq=1000;
fixedDurationPlot=false;
eyedatTrial=[10 11];
replaceOutBound=true;
saveFig=false;
plotSac=true;
plotVel=true;
plotAcc=false;
%logDir='ded014a04';
%logDir='Data/ded00800';
%logDir='data/ded005a06/';
logDir='data/juj003b06';

%% Retrieve eye tracking data
[xData,yData,pupData,info] = parseLogsEyetracking(logDir,false,false);
for i=1:info.nbTrials
    eyedat{i}=double(vertcat(xData(i,:),yData(i,:)));
end

%% Wen plotting some figures, pick your trial(s) numbers here, for instance [10] for trial 10, [10:15] for trials from 10 to 15
%% If not, set the condition to true, and it will process them all (you should remove the plotting options above in that case)
if true
      eyedatTrial=[46]; % 4 dede, 46 juju
else
    eyedatTrial=1:info.nbTrials;
end

%% Process trial (filter OutofBond, mark failedTrials)
for t=1:length(eyedatTrial)
    
    fprintf('\n### Processing trial %d\n',t);
    
    %% Values with X or Y set to minimum (-32768)
    tmpData=eyedat{eyedatTrial(t)};
    
    length(find(tmpData(1,:)==-32768));
    length(find(tmpData(2,:)==-32768));
    
    fprintf('# %d X values (out of %d) set to minimum\n',length(find(tmpData(1,:)==-32768)),length(tmpData(1,:)));
    fprintf('# %d Y values (out of %d) set to minimum\n',length(find(tmpData(2,:)==-32768)),length(tmpData(2,:)));
    
    a=find(tmpData(1,:)==-32768);
    b=find(tmpData(2,:)==-32768);
    c = [ setdiff(a,b) setdiff(b,a)];
    fprintf('# %d pairs of coordinates with only one min component\n',length(c));
    %tmpData(:,c);
    
    %% Replace outofbound by previous coordinates:
    outIndex=union(find(tmpData(1,:)==-32768),find(tmpData(2,:)==-32768));
    if replaceOutBound && ~isempty(outIndex)
        
        if isempty(outIndex)
            outOnsets=[];
            outOffsets=[];
        elseif length(outIndex)==1
            outOnsets=outIndex;
            outOffsets=outIndex;
        else
            outOnsets=[outIndex(1)];
            outOffsets=[];
        end
        for i=2:length(outIndex);
            if outIndex(i)~=outIndex(i-1)+1
                outOnsets=[outOnsets outIndex(i)];
                outOffsets=[outOffsets outIndex(i-1)];
            end
        end
        outOffsets=[outOffsets outIndex(end)];
        
        outDurations=1+outOffsets-outOnsets;
        outData=vertcat(outOnsets,outOffsets,outOffsets-outOnsets )';
        %outData
        
        for i=1:length(outOnsets)
            if outOnsets(1)==1
                continue;
            end
            tmpData(:,outOnsets(i):outOffsets(i))=repmat(tmpData(:,outOnsets(i)-1),1,outDurations(i));
        end
        eyedat{eyedatTrial(t)}=tmpData;
    end
end


%% Call Bufalo CLustering method
%  fixationstats = ClusterFix(mat2cell(eyedat{eyedatTrial},size(eyedat{eyedatTrial},1), ...
%      size(eyedat{eyedatTrial},2)),1/freq);
%   fixationstats = ClusterFix(mat2cell(eyedat{eyedatTrial},size(eyedat{eyedatTrial},1), ...
%      size(eyedat{eyedatTrial},2)),1/freq);
fixationstats = ClusterFix(eyedat(eyedatTrial),1/freq);


%% [2] Plot Scan Paths with fixations in red and saccades in green
% scale in degrees of visual angle (dva)
if plotSac == true
    for i = 1:length(fixationstats);
        xy = fixationstats{i}.XY;
        fixations = fixationstats{i}.fixations;
        fixationtimes = fixationstats{i}.fixationtimes;
        
        f=figure
        hold on
        plot(xy(1,:),xy(2,:),'g'); %green for saccades
        for ii = 1:length(fixationtimes);
            disp(ii);
            disp(fixationtimes(1,ii));
            disp(fixationtimes(2,ii));
            disp(xy(1,fixationtimes(1,ii):fixationtimes(2,ii)));
            
            plot(xy(1,fixationtimes(1,ii):fixationtimes(2,ii)),...
                xy(2,fixationtimes(1,ii):fixationtimes(2,ii)),'r'); %red for fixations
            plot(fixations(1,ii),fixations(2,ii),'k*'); %plot mean fixation location
        end
        
        csvwrite("fixations.txt", fixations);
        csvwrite("fixationtimes.txt", fixationtimes);
        csvwrite("xy.txt", xy);
        
        legend('Sacadas','Fixações')
        legend('Location','southoutside')
        
        %axis([-35000 35000 -35000 35000]);
        axis square
        %titleFig=['Saccades (' logDir ' - trial ' num2str(eyedatTrial(i)) ')'] ;
        %t=title(titleFig);
        %set(t,'Interpreter','none');
        
        %% SaveFig
        hold off
        if saveFig
            filename=titleFig;
            %filename(isspace(filename)) = []; %removing blank characters
            %filename(filename==10) = []; %removing new line characters
            folderFigures='figures';
            if ~exist(folderFigures,'dir')
                mkdir(folderFigures);
            end
            saveas(f,[folderFigures filesep filename '.fig']);
            saveas(f,[folderFigures filesep filename '.png']);
        end
    end
end

%% [3] Plot Velocity Traces with fixations in red and saccades in green

if plotVel==true
    fltord = 60; %filter order
    lowpasfrq = 30; %Low pass frequency cutoff
    nyqfrq = freq ./ 2; %nyquist frequency
    flt = fir2(fltord,[0,lowpasfrq./nyqfrq,lowpasfrq./nyqfrq,1],[1,1,0,0]); %30 Hz low pass filter
    %note when filtering scan paths for fixation detection we also use an
    %upsampling process that helps increase the signal-to-noise ratio
    
    for i = 1:length(fixationstats);
        fixationtimes = fixationstats{i}.fixationtimes;
        xy = fixationstats{i}.XY;
        
        x = xy(1,:);
        y = xy(2,:);
        x = [x(20:-1:1) x x(end:-1:end-20)]; %add 20 ms buffer for filtering
        y = [y(20:-1:1) y y(end:-1:end-20)]; %add 20 ms buffer for filtering
        x = filtfilt(flt,1,x); %filter
        y = filtfilt(flt,1,y); %filter
        x = x(21:end-20); %remove buffer after filtering
        y = y(21:end-20); %remove buffer after filtering
        
        velx = diff(xy(1,:)); %x-component of velocity
        vely = diff(xy(2,:)); %y-component of velocity
        vel = sqrt(velx.^2 + vely.^2);
        vel = vel*freq;%convert to dva  per sec since sampled at freq Hz
        
        f=figure
        plot(vel,'g'); %green for saccades
        hold on
        for ii = 1:size(fixationtimes,2);
            fixtimes = fixationtimes(1,ii):fixationtimes(2,ii);
            fixtimes(fixtimes > length(vel)) = length(vel);
            plot(fixtimes,vel(fixtimes),'r'); %red for fixations
        end
        legend('Saccades','Fixations','location','NorthEastOutside')
        ylabel('Velocity (dva/sec)')
        xlabel(['Sample (' int2str(1000/freq) ' ms/sample)'])
        box off
        if fixedDurationPlot
            xlim([1 500])
        end
        titleFig=['Velocity (' logDir ' - trial ' num2str(eyedatTrial(i)) ')'] ;
        t=title(titleFig);
        set(t,'Interpreter','none');
        
        %% SaveFig
        hold off
        if saveFig
            filename=titleFig;
            %filename(isspace(filename)) = []; %removing blank characters
            %filename(filename==10) = []; %removing new line characters
            folderFigures='figures';
            if ~exist(folderFigures,'dir')
                mkdir(folderFigures);
            end
            saveas(f,[folderFigures filesep filename '.fig']);
            saveas(f,[folderFigures filesep filename '.png']);
        end
    end
end



%% [4] Plot Acceleration Traces with fixations in red and saccades in green

if plotAcc==true
    fltord = 60; %filter order
    lowpasfrq = 30; %Low pass frequency cutoff
    nyqfrq = freq ./ 2; %nyquist frequency
    flt = fir2(fltord,[0,lowpasfrq./nyqfrq,lowpasfrq./nyqfrq,1],[1,1,0,0]); %30 Hz low pass filter
    %note when filtering scan paths for fixation detection we also use an
    %upsampling process that helps increase the signal-to-noise ratio
    
    for i = 1:length(fixationstats);
        fixationtimes = fixationstats{i}.fixationtimes;
        xy = fixationstats{i}.XY;
        
        x = xy(1,:);
        y = xy(2,:);
        x = [x(20:-1:1) x x(end:-1:end-20)]; %add 20 ms buffer for filtering
        y = [y(20:-1:1) y y(end:-1:end-20)]; %add 20 ms buffer for filtering
        x = filtfilt(flt,1,x); %filter
        y = filtfilt(flt,1,y); %filter
        x = x(21:end-20); %remove buffer after filtering
        y = y(21:end-20); %remove buffer after filtering
        
        velx = diff(xy(1,:));
        vely = diff(xy(2,:));
        vel = sqrt(velx.^2 + vely.^2);
        vel = vel;%convert to dva  per sec since sampled at freq Hz
        accel = abs(diff(vel))*freq*freq; %in dva/sec/sec
        
        f=figure
        plot(accel,'g');
        hold on
        for ii = 1:size(fixationtimes,2);
            fixtimes = fixationtimes(1,ii):fixationtimes(2,ii);
            fixtimes(fixtimes > length(accel)) = length(accel);
            plot(fixtimes,accel(fixtimes),'r'); %red for fixations
        end
        legend('Saccades','Fixations','location','NorthEastOutside')
        ylabel('Acceleration (dva/sec^2)')
        xlabel(['Sample (' int2str(1000/freq) ' ms/sample)'])
        box off
        if fixedDurationPlot
            xlim([1 500])
        end
        titleFig=['Acceleration (' logDir ' - trial ' num2str(eyedatTrial(i)) ')'] ;
        t=title(titleFig);
        set(t,'Interpreter','none');
        
        %% SaveFig
        hold off
        if saveFig
            filename=titleFig;
            %filename(isspace(filename)) = []; %removing blank characters
            %filename(filename==10) = []; %removing new line characters
            folderFigures='figures';
            if ~exist(folderFigures,'dir')
                mkdir(folderFigures);
            end
            saveas(f,[folderFigures filesep filename '.fig']);
            saveas(f,[folderFigures filesep filename '.png']);
        end
    end
end
