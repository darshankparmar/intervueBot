import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Bot,
  Brain,
  Clock,
  Target,
  Users,
  Zap,
  Upload,
  FileText,
  CheckCircle,
} from 'lucide-react';
import InterviewService, { InterviewCreate } from '../services/api';

// Validation schema
const schema = yup.object().shape({
  candidate: yup.object().shape({
    name: yup.string().required('Name is required'),
    email: yup.string().email('Invalid email').required('Email is required'),
    position: yup.string().required('Position is required'),
    experience_level: yup.string().oneOf(['junior', 'mid-level', 'senior', 'lead']).required('Experience level is required'),
    interview_type: yup.string().oneOf(['technical', 'behavioral', 'mixed', 'leadership']).required('Interview type is required'),
    files: yup.array().min(1, 'At least one file is required').required('Files are required'),
  }),
  duration_minutes: yup.number().min(30).max(120).required('Duration is required'),
});

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<InterviewCreate>({
    resolver: yupResolver(schema),
    defaultValues: {
      candidate: {
        name: '',
        email: '',
        position: '',
        experience_level: 'mid-level',
        interview_type: 'technical',
        files: [
          {
            filename: 'resume.pdf',
            file_url: 'https://example.com/resume.pdf',
            file_type: 'resume' as const,
          }
        ],
      },
      duration_minutes: 60,
    },
  });

  const onSubmit = async (data: InterviewCreate) => {
    setLoading(true);
    setError(null);

    try {
      const response = await InterviewService.startInterview(data);
      navigate(`/interview/${response.session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start interview');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: <Brain size={32} />,
      title: 'AI-Powered Interviews',
      description: 'Intelligent question generation and adaptive difficulty based on candidate responses',
    },
    {
      icon: <Target size={32} />,
      title: 'Resume Analysis',
      description: 'Automated analysis of resumes and CVs to extract skills and experience',
    },
    {
      icon: <Clock size={32} />,
      title: 'Real-time Evaluation',
      description: 'Instant feedback and scoring with detailed performance metrics',
    },
    {
      icon: <Users size={32} />,
      title: 'Multi-format Support',
      description: 'Support for PDF, DOC, DOCX, and TXT files for comprehensive analysis',
    },
    {
      icon: <Zap size={32} />,
      title: 'Adaptive Questions',
      description: 'Dynamic question generation that adapts to candidate performance',
    },
    {
      icon: <CheckCircle size={32} />,
      title: 'Comprehensive Reports',
      description: 'Detailed evaluation reports with hiring recommendations',
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box textAlign="center" mb={6}>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
              <Bot size={64} color="#6366f1" />
            </Box>
            <Typography variant="h2" gutterBottom sx={{ fontWeight: 700 }}>
              Welcome to IntervueBot
            </Typography>
            <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
              AI-Powered Interview Platform for Intelligent Candidate Assessment
            </Typography>
          </motion.div>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
          {/* Features Section */}
          <Box sx={{ flex: { xs: '1', md: '0 0 33.333%' } }}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)', height: '100%' }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                    Key Features
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    {features.map((feature, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                          <Box sx={{ color: 'primary.main', mt: 0.5 }}>
                            {feature.icon}
                          </Box>
                          <Box>
                            <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                              {feature.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {feature.description}
                            </Typography>
                          </Box>
                        </Box>
                      </motion.div>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Box>

          {/* Interview Form */}
          <Box sx={{ flex: { xs: '1', md: '0 0 66.666%' } }}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
                <CardContent>
                  <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
                    Start Your Interview
                  </Typography>

                  {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                      {error}
                    </Alert>
                  )}

                  <form onSubmit={handleSubmit(onSubmit)}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      {/* Basic Information */}
                      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3 }}>
                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.name"
                            control={control}
                            render={({ field }) => (
                              <TextField
                                {...field}
                                label="Full Name"
                                fullWidth
                                error={!!errors.candidate?.name}
                                helperText={errors.candidate?.name?.message}
                                sx={{ mb: 2 }}
                              />
                            )}
                          />
                        </Box>

                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.email"
                            control={control}
                            render={({ field }) => (
                              <TextField
                                {...field}
                                label="Email Address"
                                type="email"
                                fullWidth
                                error={!!errors.candidate?.email}
                                helperText={errors.candidate?.email?.message}
                                sx={{ mb: 2 }}
                              />
                            )}
                          />
                        </Box>
                      </Box>

                      <Box>
                        <Controller
                          name="candidate.position"
                          control={control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              label="Position Applied For"
                              fullWidth
                              error={!!errors.candidate?.position}
                              helperText={errors.candidate?.position?.message}
                              sx={{ mb: 2 }}
                            />
                          )}
                        />
                      </Box>

                      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 3 }}>
                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.experience_level"
                            control={control}
                            render={({ field }) => (
                              <FormControl fullWidth error={!!errors.candidate?.experience_level}>
                                <InputLabel>Experience Level</InputLabel>
                                <Select {...field} label="Experience Level">
                                  <MenuItem value="junior">Junior (0-2 years)</MenuItem>
                                  <MenuItem value="mid-level">Mid-Level (3-5 years)</MenuItem>
                                  <MenuItem value="senior">Senior (6-8 years)</MenuItem>
                                  <MenuItem value="lead">Lead (9+ years)</MenuItem>
                                </Select>
                                {errors.candidate?.experience_level && (
                                  <Typography variant="caption" color="error">
                                    {errors.candidate.experience_level.message}
                                  </Typography>
                                )}
                              </FormControl>
                            )}
                          />
                        </Box>

                        <Box sx={{ flex: 1 }}>
                          <Controller
                            name="candidate.interview_type"
                            control={control}
                            render={({ field }) => (
                              <FormControl fullWidth error={!!errors.candidate?.interview_type}>
                                <InputLabel>Interview Type</InputLabel>
                                <Select {...field} label="Interview Type">
                                  <MenuItem value="technical">Technical</MenuItem>
                                  <MenuItem value="behavioral">Behavioral</MenuItem>
                                  <MenuItem value="mixed">Mixed</MenuItem>
                                  <MenuItem value="leadership">Leadership</MenuItem>
                                </Select>
                                {errors.candidate?.interview_type && (
                                  <Typography variant="caption" color="error">
                                    {errors.candidate.interview_type.message}
                                  </Typography>
                                )}
                              </FormControl>
                            )}
                          />
                        </Box>
                      </Box>

                      <Box>
                        <Controller
                          name="duration_minutes"
                          control={control}
                          render={({ field }) => (
                            <TextField
                              {...field}
                              label="Interview Duration (minutes)"
                              type="number"
                              fullWidth
                              error={!!errors.duration_minutes}
                              helperText={errors.duration_minutes?.message}
                              sx={{ mb: 2 }}
                            />
                          )}
                        />
                      </Box>

                      {/* File Upload Section */}
                      <Box>
                        <Paper
                          sx={{
                            p: 3,
                            border: '2px dashed',
                            borderColor: 'primary.main',
                            backgroundColor: 'rgba(99, 102, 241, 0.05)',
                            textAlign: 'center',
                          }}
                        >
                          <Upload size={48} color="#6366f1" style={{ marginBottom: 16 }} />
                          <Typography variant="h6" gutterBottom>
                            Upload Resume & Documents
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Drag and drop your resume, CV, or cover letter files here
                          </Typography>
                          <Button
                            variant="outlined"
                            startIcon={<FileText />}
                            sx={{ mt: 2 }}
                          >
                            Choose Files
                          </Button>
                          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                            Supported formats: PDF, DOC, DOCX, TXT (Max 10MB each)
                          </Typography>
                        </Paper>
                      </Box>

                      {/* Submit Button */}
                      <Box>
                        <Button
                          type="submit"
                          variant="contained"
                          size="large"
                          fullWidth
                          disabled={loading}
                          sx={{
                            py: 2,
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                            '&:hover': {
                              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                            },
                          }}
                        >
                          {loading ? (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <CircularProgress size={20} color="inherit" />
                              Starting Interview...
                            </Box>
                          ) : (
                            'Start Interview'
                          )}
                        </Button>
                      </Box>
                    </Box>
                  </form>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Box>
      </motion.div>
    </Container>
  );
};

export default HomePage; 