function computeflow(root)
    % Add path to optical flow package
    mex_dir = '';
    addpath(mex_dir);

    alpha = 0.012;
    ratio = 0.75;
    minWidth = 20;
    nOuterFPIterations = 7;
    nInnerFPIterations = 1;
    nSORIterations = 30;

    para = [alpha,ratio,minWidth,nOuterFPIterations,nInnerFPIterations,nSORIterations];

    frames_folder = sprintf('%s/frames/',root);
    nframes = length(dir(frames_folder)) - 2;
    for i = 1:nframes-1
        image1 = [frames_folder, sprintf('%d.jpg',i)];
        image2 = [frames_folder, sprintf('%d.jpg',i+1)];
        outputpath = [sprintf('%s/flow/',root), sprintf('%d.flo',i)];
        if exist(outputpath, 'file') > 0
            continue
        end

        im1 = im2double(imread(image1));
        im2 = im2double(imread(image2));

        [vx,vy,warpI2] = Coarse2FineTwoFrames(im1,im2,para);

        [height, width] = size(vx);
        img = zeros(height,width,2);
        img(:,:,1) = vx;
        img(:,:,2) = vy;
        writeFlowFile(img, outputpath);

        if mod(i,100) == 0
            fprintf('Processed %d images\n',i)
        end
    end
end

function writeFlowFile(img, filename)
    TAG_STRING = 'PIEH';    % use this when WRITING the file

    [height width nBands] = size(img);

    if nBands ~= 2
        error('writeFlowFile: image must have two bands');    
    end;    

    fid = fopen(filename, 'w');
    if (fid < 0)
        error('writeFlowFile: could not open %s', filename);
    end;

    % write the header
    fwrite(fid, TAG_STRING); 
    fwrite(fid, width, 'int32');
    fwrite(fid, height, 'int32');

    % arrange into matrix form
    tmp = zeros(height, width*nBands);

    tmp(:, (1:width)*nBands-1) = img(:,:,1);
    tmp(:, (1:width)*nBands) = squeeze(img(:,:,2));
    tmp = tmp';

    fwrite(fid, tmp, 'float32');
    fclose(fid);
end
