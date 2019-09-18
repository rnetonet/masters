function val = subindex(array, varargin)
%SUBINDEX Access directly elements of an array returned by a function
%
%    val = subindex(array, varargin)
%
%      array                 - input array
%      varargin              - subscript arrays or index to access
%
%    Examples :  subindex(rand(3),1,3)
%                subindex(rand(3),1,:)
%
%   Author:      Adrien Brilhault
%   Date:        2017-06-15
%   E-mail:      adrien.brilhault@gmail.com
%
%

%%comment next line to cancel automatic expansion
varargin(end+1:ndims(array))={':'};

val = subsref(array, struct('type','()', 'subs', {varargin}));

%% See this other example with cell in MultiRes
%resStats(i)=computeStats(cellfun(@(x) subsref(x,struct('type','()','subs',{{':',i}})),recInterpolated,'UniformOutput',false));
