import React, { useEffect, useState } from 'react';
import { authApi } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import { API_BASE_URL } from '../config';
import { Card, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Label } from './ui/Label';
import { AlertCircle, User, Mail, Lock, ShieldCheck, Eye, EyeOff, MapPin, Zap, Activity, BarChart3, Globe } from 'lucide-react';

export const AuthForm: React.FC = () => {
  const { setUser, refreshUser } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const authError = params.get('auth_error');
    if (authError) {
      const messages: Record<string, string> = {
        cancelled: 'Sign-in was cancelled. Please try again.',
        google_error: 'Google returned an error. Please try again.',
        state_mismatch: 'Security check failed. Please try again.',
        missing_code: 'Authorization code missing. Please try again.',
        token_exchange_failed: 'Could not complete sign-in. Please try again.',
        identity_verification_failed: 'Google identity could not be verified.',
        duplicate_account: 'An account with this email already exists.',
        account_disabled: 'This account has been disabled.',
        service_unavailable: 'Service temporarily unavailable.',
      };
      setError(messages[authError] || 'Authentication failed. Please try again.');
      window.history.replaceState({}, '', '/');
    }
  }, []);

  const handleGoogleSignIn = () => {
    setLoading(true);
    window.location.href = `${API_BASE_URL}/api/v1/auth/google/start`;
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        if (!displayName.trim()) {
          throw new Error('Display name is required for registration.');
        }
        await authApi.register({ email, password, display_name: displayName });
      }
      
      const session = await authApi.login({ email, password });
      setUser(session);
      await refreshUser();
      
      if (session.role === 'authority' || session.role === 'admin') {
        window.location.href = '/authority';
      } else {
        window.location.href = '/dashboard';
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex w-full bg-white font-sans">
      
      {/* LEFT SIDE: Landing & Product Info */}
      <div className="hidden lg:flex flex-col w-1/2 bg-white relative p-12 lg:p-16 xl:p-20 border-r border-slate-100 overflow-y-auto">
        
        {/* Navigation */}
        <nav className="flex items-center justify-between w-full mb-16">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <MapPin className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 leading-tight">CivicPulse AI</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Smart Civic Intelligence</p>
            </div>
          </div>
          <div className="hidden xl:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#" className="text-slate-900 font-bold">Home</a>
            <a href="#" className="hover:text-indigo-600 transition-colors">Features</a>
            <a href="#" className="hover:text-indigo-600 transition-colors">How It Works</a>
            <a href="#" className="hover:text-indigo-600 transition-colors">About Us</a>
          </div>
          <div className="flex flex-shrink-0 items-center gap-4">
            <div className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 rounded-full text-xs font-medium text-slate-600 hover:bg-slate-50 cursor-pointer">
              <Globe className="h-3.5 w-3.5" /> English
            </div>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="max-w-xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-semibold uppercase tracking-wider mb-6">
            <Zap className="h-3.5 w-3.5" /> AI-Powered Civic Platform
          </div>
          <h2 className="text-5xl xl:text-6xl font-bold text-slate-900 leading-[1.1] tracking-tight mb-6">
            Building Better <br />
            <span className="text-indigo-600">Communities Together</span>
          </h2>
          <p className="text-lg text-slate-600 mb-12 leading-relaxed max-w-lg">
            Report civic issues, track progress, and help your city become smarter with AI-powered insights and real-time updates.
          </p>

          {/* Features */}
          <div className="space-y-8 mb-16">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-blue-50 rounded-xl text-blue-600 mt-1">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900">Report Issues Easily</h3>
                <p className="text-sm text-slate-500 mt-1">Submit complaints with photos and verified location data.</p>
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="p-3 bg-emerald-50 rounded-xl text-emerald-600 mt-1">
                <Activity className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900">AI-Powered Analysis</h3>
                <p className="text-sm text-slate-500 mt-1">Smart category classification and severity detection.</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-3 bg-amber-50 rounded-xl text-amber-600 mt-1">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900">Track Real-time Progress</h3>
                <p className="text-sm text-slate-500 mt-1">Stay updated with status changes and authority responses.</p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="p-3 bg-purple-50 rounded-xl text-purple-600 mt-1">
                <BarChart3 className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900">Data-Driven Insights</h3>
                <p className="text-sm text-slate-500 mt-1">Helping authorities make better decisions via predictive analysis.</p>
              </div>
            </div>
          </div>

          {/* Static Trust Banner */}
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-4">
              <div className="bg-white p-2.5 rounded-full border border-slate-200 shadow-sm">
                <ShieldCheck className="h-6 w-6 text-indigo-600" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm">Secure & Private</h4>
                <p className="text-xs text-slate-500 mt-0.5">Your civic data is protected and used responsibly.</p>
              </div>
            </div>
            <div className="hidden sm:block border-l border-slate-200 h-10 mx-4"></div>
            <div className="hidden sm:block text-right">
              <p className="font-bold text-slate-900 text-sm">Real-time Platform</p>
              <p className="text-xs text-slate-500 mt-0.5">Verified civic intelligence.</p>
            </div>
          </div>
        </div>
      </div>


      {/* RIGHT SIDE: Auth Form */}
      <div className="w-full lg:w-1/2 bg-slate-50 flex flex-col justify-center items-center p-4 sm:p-8 relative">
        
        {/* Mobile Header (Only visible on small screens) */}
        <div className="lg:hidden absolute top-6 left-6 flex items-center gap-2">
          <div className="bg-indigo-600 p-1.5 rounded-md">
            <MapPin className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold text-slate-900">CivicPulse AI</span>
        </div>

        <div className="w-full max-w-[440px]">
          <Card className="border-0 shadow-2xl rounded-3xl overflow-hidden bg-white animate-in fade-in zoom-in-95 duration-500">
            <CardContent className="p-0">
              
              {/* Tab Selector */}
              <div className="flex border-b border-slate-100">
                <button
                  onClick={() => { setIsRegister(false); setError(null); }}
                  className={`flex-1 py-4 text-sm font-semibold transition-colors relative ${!isRegister ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-800'}`}
                >
                  Log In
                  {!isRegister && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600" />}
                </button>
                <button
                  onClick={() => { setIsRegister(true); setError(null); }}
                  className={`flex-1 py-4 text-sm font-semibold transition-colors relative ${isRegister ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-800'}`}
                >
                  Register
                  {isRegister && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600" />}
                </button>
              </div>

              <div className="p-8 sm:p-10 space-y-6">
                <div className="text-center space-y-2 mb-8">
                  <h2 className="text-2xl font-bold text-slate-900">
                    {isRegister ? 'Create an Account' : 'Welcome Back! 👋'}
                  </h2>
                  <p className="text-sm text-slate-500">
                    {isRegister ? 'Join CivicPulse to start reporting issues.' : 'Log in to continue to CivicPulse AI.'}
                  </p>
                </div>

                {error && (
                  <div className="p-3 rounded-xl bg-red-50 border border-red-100 flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800 font-medium leading-snug">{error}</p>
                  </div>
                )}

                {/* Google Auth */}
                <Button 
                  type="button"
                  onClick={handleGoogleSignIn}
                  disabled={loading}
                  variant="outline"
                  className="w-full h-12 relative bg-white hover:bg-slate-50 text-slate-700 border-slate-200 font-semibold rounded-xl transition-all shadow-sm"
                >
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center justify-center">
                    <svg className="w-5 h-5" viewBox="0 0 48 48">
                      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                    </svg>
                  </div>
                  Continue with Google
                </Button>

                <div className="relative flex items-center py-2">
                  <div className="flex-grow border-t border-slate-100"></div>
                  <span className="flex-shrink-0 mx-4 text-xs font-medium text-slate-400">or continue with email</span>
                  <div className="flex-grow border-t border-slate-100"></div>
                </div>

                <form onSubmit={handleEmailSubmit} className="space-y-4">
                  {isRegister && (
                    <div className="space-y-1.5">
                      <Label htmlFor="displayName" className="text-sm font-semibold text-slate-700">
                        Full Name
                      </Label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                          <User className="h-5 w-5 text-slate-400" />
                        </div>
                        <Input
                          id="displayName"
                          type="text"
                          required
                          value={displayName}
                          onChange={(e: any) => setDisplayName(e.target.value)}
                          placeholder="John Doe"
                          className="pl-11 h-12 bg-white border-slate-200 focus:bg-white focus:border-indigo-500 rounded-xl transition-all shadow-sm"
                        />
                      </div>
                    </div>
                  )}

                  <div className="space-y-1.5">
                    <Label htmlFor="email" className="text-sm font-semibold text-slate-700">
                      Email Address
                    </Label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-slate-400" />
                      </div>
                      <Input
                        id="email"
                        type="email"
                        required
                        value={email}
                        onChange={(e: any) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        className="pl-11 h-12 bg-white border-slate-200 focus:bg-white focus:border-indigo-500 rounded-xl transition-all shadow-sm"
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center">
                      <Label htmlFor="password" className="text-sm font-semibold text-slate-700">
                        Password
                      </Label>
                    </div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-slate-400" />
                      </div>
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        required
                        minLength={isRegister ? 8 : 1}
                        value={password}
                        onChange={(e: any) => setPassword(e.target.value)}
                        placeholder="Enter your password"
                        className="pl-11 pr-11 h-12 bg-white border-slate-200 focus:bg-white focus:border-indigo-500 rounded-xl transition-all shadow-sm"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600"
                        aria-label={showPassword ? "Hide password" : "Show password"}
                      >
                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>
                    {isRegister && <p className="text-xs text-slate-500 mt-1">Must be at least 8 characters.</p>}
                  </div>

                  {!isRegister && (
                    <div className="flex justify-end pt-1 pb-2">
                      <a href="#" className="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors">
                        Forgot Password?
                      </a>
                    </div>
                  )}

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-12 mt-2 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white font-bold rounded-xl shadow-md hover:shadow-lg transition-all"
                  >
                    {loading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        {isRegister ? 'Creating Account...' : 'Logging In...'}
                      </div>
                    ) : (
                      isRegister ? 'Create Account' : 'Log In'
                    )}
                  </Button>
                </form>
              </div>
              
              <div className="bg-slate-50 border-t border-slate-100 p-6 flex flex-col items-center justify-center gap-4 text-center">
                <button
                  type="button"
                  onClick={() => { setIsRegister(!isRegister); setError(null); }}
                  className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors"
                >
                  {isRegister ? (
                    <>Already have an account? <span className="text-indigo-600 font-bold">Log in</span></>
                  ) : (
                    <>New to CivicPulse AI? <span className="text-indigo-600 font-bold">Create an account</span></>
                  )}
                </button>
              </div>
            </CardContent>
          </Card>

          {/* Footer Text */}
          <div className="mt-8 text-center flex items-center justify-center gap-2 text-sm text-slate-500">
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
            Trusted by citizens and authorities for secure reporting
          </div>
        </div>
      </div>

    </div>
  );
};
