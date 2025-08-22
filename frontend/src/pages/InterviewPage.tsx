import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Alert,
  CircularProgress,
  Paper,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Clock,
  Send,
  CheckCircle,
  AlertCircle,
  Target,
  TrendingUp,
  Timer,
  User,
  FileText,
} from 'lucide-react';
import InterviewService, { Question, ResponseEvaluation } from '../services/api';

const InterviewPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<ResponseEvaluation | null>(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [questionNumber, setQuestionNumber] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);

  const didFetch = React.useRef(false);

  useEffect(() => {
    if (sessionId && !didFetch.current) {
      didFetch.current = true;
      loadNextQuestion();
    }
  }, [sessionId]);

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && currentQuestion && !submitting) {
      // Time ran out - auto-submit empty response and end interview
      handleTimeoutExpired();
    }
  }, [timeLeft, currentQuestion, submitting]);

  const handleTimeoutExpired = async () => {
    if (!sessionId || !currentQuestion) return;

    console.log('Time expired, auto-submitting empty response and ending interview');
    setSubmitting(true);
    setError(null);

    try {
      // Submit empty response to indicate timeout
      await InterviewService.submitResponse(sessionId, {
        question_id: currentQuestion.id,
        answer: "[No response - time expired]",
        time_taken: currentQuestion.expected_duration,
      });

      // Show timeout message
      setError("Time expired! Your interview has been automatically ended due to no response.");

      // Auto-finalize interview after 5 seconds
      setTimeout(async () => {
        try {
          await InterviewService.finalizeInterview(sessionId);
          navigate(`/report/${sessionId}`);
        } catch (err) {
          console.error('Failed to auto-finalize interview:', err);
          setError('Interview ended due to timeout. Please contact support for your results.');
        }
      }, 5000);

    } catch (err) {
      console.error('Failed to submit timeout response:', err);
      setError('Interview ended due to timeout. Please contact support for your results.');
    } finally {
      setSubmitting(false);
    }
  };

  const loadNextQuestion = async () => {
    if (!sessionId) {
      console.log('No sessionId available');
      return;
    }

    if (loading) {
      return;
    }

    console.log('Loading next question for session:', sessionId);
    setLoading(true);
    setError(null);
    setEvaluation(null);

    try {
      const questionData = await InterviewService.getNextQuestion(sessionId);
      console.log('Next question loaded:', questionData);
      setCurrentQuestion(questionData.question);
      setTimeLeft(questionData.time_limit);
      setQuestionNumber(questionData.question_number);
      setTotalQuestions(questionData.question_number + 5); // Estimate
    } catch (err) {
      console.error('Error loading next question:', err);
      setError(err instanceof Error ? err.message : 'Failed to load question');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitResponse = async () => {
    if (!sessionId || !currentQuestion || !response.trim()) return;

    // If response is empty, fill with default text
    const answerToSend = response.trim() ? response : '[Not answered]';

    setSubmitting(true);
    setError(null);

    try {
      const evaluationData = await InterviewService.submitResponse(sessionId, {
        question_id: currentQuestion.id,
        answer: answerToSend,
        time_taken: currentQuestion.expected_duration - timeLeft,
      });

      setEvaluation(evaluationData.evaluation);
      setResponse('');

      console.log('Response submitted successfully, scheduling next question...');

      // Auto-advance to next question after 5 seconds
      setTimeout(() => {
        console.log('Timeout triggered, loading next question...');
        loadNextQuestion();
      }, 5000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFinalizeInterview = async () => {
    if (!sessionId) return;

    try {
      await InterviewService.finalizeInterview(sessionId);
      navigate(`/report/${sessionId}`, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to finalize interview');
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'success';
    if (score >= 6) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box textAlign="center">
          <CircularProgress size={60} sx={{ mb: 2 }} />
          <Typography variant="h6">Loading next question...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
              Question {questionNumber}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {currentQuestion?.category} • {currentQuestion?.difficulty} difficulty
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              icon={<Timer />}
              label={formatTime(timeLeft)}
              color={timeLeft < 30 ? 'error' : timeLeft < 60 ? 'warning' : 'primary'}
              variant="outlined"
              sx={{
                animation: timeLeft < 30 ? 'pulse 1s infinite' : 'none',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                  '100%': { opacity: 1 },
                }
              }}
            />
            {timeLeft < 60 && (
              <Alert severity="warning" sx={{ py: 0 }}>
                Time running out!
              </Alert>
            )}
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleFinalizeInterview}
            >
              End Interview
            </Button>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
          {/* Question Section */}
          <Box sx={{ flex: { xs: '1', md: '0 0 66.666%' } }}>
            <AnimatePresence mode="wait">
              {loading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <Box textAlign="center">
                    <CircularProgress size={60} />
                  </Box>
                </motion.div>
              ) : currentQuestion ? (
                <motion.div
                  key={currentQuestion.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.5 }}
                >
                  <Card sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {currentQuestion?.text}
                      </Typography>

                      {/* Time Progress Bar */}
                      <Box sx={{ mt: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            Time Remaining
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {formatTime(timeLeft)}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={(timeLeft / (currentQuestion?.expected_duration || 300)) * 100}
                          color={timeLeft < 30 ? 'error' : timeLeft < 60 ? 'warning' : 'primary'}
                          sx={{ height: 8, borderRadius: 4 }}
                        />

                        {/* Time Warning Messages */}
                        {timeLeft < 30 && (
                          <Alert severity="error" sx={{ mt: 1, py: 0 }}>
                            ⚠️ Time is almost up! Please submit your answer quickly.
                          </Alert>
                        )}
                        {timeLeft < 60 && timeLeft >= 30 && (
                          <Alert severity="warning" sx={{ mt: 1, py: 0 }}>
                            ⏰ Less than 1 minute remaining!
                          </Alert>
                        )}
                      </Box>

                      {/* Question Context */}
                      {currentQuestion?.context && (
                        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Focus Area:</strong> {currentQuestion.context.focus_area}
                          </Typography>
                          {currentQuestion.context.reasoning && (
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              <strong>Context:</strong> {currentQuestion.context.reasoning}
                            </Typography>
                          )}
                        </Box>
                      )}

                      <TextField
                        multiline
                        rows={6}
                        fullWidth
                        label="Your Answer"
                        value={response}
                        onChange={(e) => setResponse(e.target.value)}
                        disabled={submitting}
                        sx={{ mb: 3 }}
                      />

                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                          variant="contained"
                          size="large"
                          onClick={handleSubmitResponse}
                          disabled={!response.trim() || submitting}
                          startIcon={<Send />}
                          sx={{ flex: 1 }}
                        >
                          {submitting ? 'Submitting...' : 'Submit Answer'}
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              ) : null}
            </AnimatePresence>

            {/* Evaluation Section */}
            {evaluation && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      Response Evaluation
                    </Typography>

                    {/* Overall Score */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                      <Box sx={{ mr: 2 }}>
                        <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
                          {evaluation.overall_score}/10
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={evaluation.overall_score * 10}
                          sx={{ height: 12, borderRadius: 6 }}
                        />
                      </Box>
                    </Box>

                    {/* Detailed Scores */}
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, mb: 3 }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Technical Accuracy
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {evaluation.technical_accuracy}/10
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Communication
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {evaluation.communication_clarity}/10
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Problem Solving
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {evaluation.problem_solving_approach}/10
                        </Typography>
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Experience Relevance
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {evaluation.experience_relevance}/10
                        </Typography>
                      </Box>
                    </Box>

                    {/* Feedback */}
                    <Divider sx={{ my: 2 }} />

                    {evaluation.strengths.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'success.main', mb: 1 }}>
                          Strengths
                        </Typography>
                        <List dense>
                          {evaluation.strengths.map((strength, index) => (
                            <ListItem key={index} sx={{ py: 0.5 }}>
                              <ListItemIcon sx={{ minWidth: 32 }}>
                                <CheckCircle size={16} color="#10b981" />
                              </ListItemIcon>
                              <ListItemText primary={strength} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}

                    {evaluation.areas_for_improvement.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'warning.main', mb: 1 }}>
                          Areas for Improvement
                        </Typography>
                        <List dense>
                          {evaluation.areas_for_improvement.map((area, index) => (
                            <ListItem key={index} sx={{ py: 0.5 }}>
                              <ListItemIcon sx={{ minWidth: 32 }}>
                                <AlertCircle size={16} color="#f59e0b" />
                              </ListItemIcon>
                              <ListItemText primary={area} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </Box>

          {/* Sidebar */}
          <Box sx={{ flex: { xs: '1', md: '0 0 33.333%' } }}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)', mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Interview Progress
                  </Typography>

                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Progress</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {Math.round((questionNumber / totalQuestions) * 100)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(questionNumber / totalQuestions) * 100}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">Question</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {questionNumber} of {totalQuestions}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">Time Remaining</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {formatTime(timeLeft)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>

              <Card sx={{ background: 'rgba(255, 255, 255, 0.9)' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Question Details
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Category
                    </Typography>
                    <Chip
                      label={currentQuestion?.category || 'General'}
                      color="primary"
                      size="small"
                      sx={{ mt: 0.5 }}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Difficulty
                    </Typography>
                    <Chip
                      label={currentQuestion?.difficulty || 'Medium'}
                      color={currentQuestion?.difficulty === 'hard' ? 'error' :
                        currentQuestion?.difficulty === 'easy' ? 'success' : 'warning'}
                      size="small"
                      sx={{ mt: 0.5 }}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Expected Duration
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {Math.round((currentQuestion?.expected_duration || 300) / 60)} minutes
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Box>
      </motion.div>
    </Container>
  );
};

export default InterviewPage; 