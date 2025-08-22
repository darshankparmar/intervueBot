import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  X,
  CheckCircle,
  AlertCircle,
  File,
  FileImage,
  FileCode,
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  fileType: 'resume' | 'cv' | 'cover_letter';
  content: string;
  status: 'uploading' | 'success' | 'error';
  error?: string;
}

interface FileUploadProps {
  onFilesChange: (files: UploadedFile[]) => void;
  maxFiles?: number;
  maxSize?: number; // in bytes
  acceptedFileTypes?: string[];
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFilesChange,
  maxFiles = 10,
  maxSize = 10 * 1024 * 1024, // 10MB
  acceptedFileTypes = ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setError(null);

      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const errors = rejectedFiles.map(({ file, errors }) => {
          const errorMessages = errors.map((error: any) => {
            switch (error.code) {
              case 'file-too-large':
                return `File too large (max ${maxSize / 1024 / 1024}MB)`;
              case 'file-invalid-type':
                return 'File type not supported';
              case 'too-many-files':
                return `Too many files (max ${maxFiles})`;
              default:
                return error.message;
            }
          });
          return `${file.name}: ${errorMessages.join(', ')}`;
        });
        setError(errors.join('; '));
        return;
      }

      // Check if adding these files would exceed the limit
      if (uploadedFiles.length + acceptedFiles.length > maxFiles) {
        setError(`Too many files. Maximum ${maxFiles} files allowed.`);
        return;
      }

      // Process accepted files
      const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        fileType: determineFileType(file.name),
        content: '',
        status: 'uploading',
      }));

      // Read file contents
      newFiles.forEach(async (fileInfo, index) => {
        try {
          const file = acceptedFiles[index];
          const content = await readFileAsBase64(file);
          
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileInfo.id 
                ? { ...f, content, status: 'success' as const }
                : f
            )
          );
        } catch (error) {
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileInfo.id 
                ? { ...f, status: 'error' as const, error: 'Failed to read file' }
                : f
            )
          );
        }
      });

      setUploadedFiles(prev => [...prev, ...newFiles]);
    },
    [uploadedFiles, maxFiles, maxSize]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'application/rtf': ['.rtf'],
    },
    maxSize,
    maxFiles: maxFiles - uploadedFiles.length,
  });

  const readFileAsBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const determineFileType = (filename: string): 'resume' | 'cv' | 'cover_letter' => {
    const lowerName = filename.toLowerCase();
    if (lowerName.includes('cv') || lowerName.includes('curriculum')) {
      return 'cv';
    } else if (lowerName.includes('cover') || lowerName.includes('letter')) {
      return 'cover_letter';
    } else {
      return 'resume';
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const updateFileType = (fileId: string, newType: 'resume' | 'cv' | 'cover_letter') => {
    setUploadedFiles(prev => 
      prev.map(f => f.id === fileId ? { ...f, fileType: newType } : f)
    );
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FileText size={20} color="#dc2626" />;
      case 'doc':
      case 'docx':
        return <FileText size={20} color="#2563eb" />;
      case 'txt':
        return <FileText size={20} color="#059669" />;
      case 'rtf':
        return <FileText size={20} color="#7c3aed" />;
      default:
        return <File size={20} color="#6b7280" />;
    }
  };

  const getFileTypeColor = (fileType: string) => {
    switch (fileType) {
      case 'resume':
        return 'primary';
      case 'cv':
        return 'secondary';
      case 'cover_letter':
        return 'success';
      default:
        return 'default';
    }
  };

  // Update parent component when files change
  React.useEffect(() => {
    onFilesChange(uploadedFiles);
  }, [uploadedFiles, onFilesChange]);

  return (
    <Box>
      {/* Error Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Area */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'rgba(99, 102, 241, 0.05)' : 'transparent',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'rgba(99, 102, 241, 0.05)',
          },
        }}
      >
        <input {...getInputProps()} />
        <Upload size={48} color="#6366f1" style={{ marginBottom: 16 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop files here' : 'Upload Resume & Documents'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Drag and drop your resume, CV, or cover letter files here
        </Typography>
        <Button
          variant="outlined"
          startIcon={<FileText />}
          sx={{ mt: 2 }}
          onClick={() => fileInputRef.current?.click()}
        >
          Choose Files
        </Button>
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          Supported formats: PDF, DOC, DOCX, TXT, RTF (Max {maxSize / 1024 / 1024}MB each)
        </Typography>
      </Paper>

      {/* Upload Progress */}
      <AnimatePresence>
        {isUploading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Uploading files... {uploadProgress}%
              </Typography>
              <LinearProgress variant="determinate" value={uploadProgress} />
            </Box>
          </motion.div>
        )}
      </AnimatePresence>

      {/* File List */}
      <AnimatePresence>
        {uploadedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Uploaded Files ({uploadedFiles.length}/{maxFiles})
              </Typography>
              
              <List>
                {uploadedFiles.map((file) => (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <ListItem
                      sx={{
                        border: '1px solid',
                        borderColor: 'grey.200',
                        borderRadius: 1,
                        mb: 1,
                        backgroundColor: 'background.paper',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                        {file.status === 'success' ? (
                          <CheckCircle size={20} color="#10b981" />
                        ) : file.status === 'error' ? (
                          <AlertCircle size={20} color="#ef4444" />
                        ) : (
                          <Box sx={{ width: 20, height: 20, borderRadius: '50%', backgroundColor: 'grey.300' }} />
                        )}
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                        {getFileIcon(file.name)}
                      </Box>
                      
                      <ListItemText
                        primary={file.name}
                        secondary={`${formatFileSize(file.size)} • ${file.status}`}
                      />
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={file.fileType.replace('_', ' ')}
                          color={getFileTypeColor(file.fileType) as any}
                          size="small"
                          onClick={() => {
                            const types: ('resume' | 'cv' | 'cover_letter')[] = ['resume', 'cv', 'cover_letter'];
                            const currentIndex = types.indexOf(file.fileType);
                            const nextType = types[(currentIndex + 1) % types.length];
                            updateFileType(file.id, nextType);
                          }}
                          sx={{ cursor: 'pointer' }}
                        />
                        
                        <IconButton
                          size="small"
                          onClick={() => removeFile(file.id)}
                          sx={{ color: 'error.main' }}
                        >
                          <X size={16} />
                        </IconButton>
                      </Box>
                    </ListItem>
                  </motion.div>
                ))}
              </List>
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
};

export default FileUpload; 