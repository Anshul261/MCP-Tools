'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { BrainIcon, SparklesIcon, ZapIcon, HardDriveIcon, EyeIcon, EyeOffIcon, MailIcon, LockIcon, ArrowRightIcon } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentTextIndex, setCurrentTextIndex] = useState(0)
  const [showPassword, setShowPassword] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)
  const router = useRouter()

  const rotatingTexts = [
    { text: "AI-Powered Search", icon: <BrainIcon className="h-5 w-5" />, gradient: "from-blue-500 to-purple-600" },
    { text: "Intelligent Analysis", icon: <SparklesIcon className="h-5 w-5" />, gradient: "from-orange-500 to-pink-600" },
    { text: "Lightning Fast", icon: <ZapIcon className="h-5 w-5" />, gradient: "from-green-500 to-teal-600" },
    { text: "Local Knowledge", icon: <HardDriveIcon className="h-5 w-5" />, gradient: "from-gray-500 to-slate-600" },
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTextIndex((prev) => (prev + 1) % rotatingTexts.length)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // For demo purposes, accept any email/password
    if (email && password) {
      router.push('/chat')
    }
    
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-background via-background-secondary to-background relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary/20 to-primary-hover/20 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-primary/15 to-primary-hover/15 rounded-full blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, 50, 0],
            scale: [1.2, 1, 1.2],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Additional Background Elements */}
        <motion.div
          className="absolute top-1/4 left-1/4 w-2 h-2 bg-primary/40 rounded-full"
          animate={{
            scale: [1, 2, 1],
            opacity: [0.4, 0.8, 0.4],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute top-3/4 right-1/3 w-1 h-1 bg-primary-hover/60 rounded-full"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.6, 1, 0.6],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        />
      </div>

      {/* Left Side - Branding */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="hidden lg:flex lg:w-1/2 items-center justify-center p-12 relative z-10"
      >
        <div className="max-w-lg">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-8"
          >
            <h1 className="text-5xl font-bold text-foreground mb-4 leading-tight">
              Welcome to{' '}
              <span className="bg-gradient-to-r from-primary to-primary-hover bg-clip-text text-transparent">
                AI Chat
              </span>
            </h1>
            <p className="text-xl text-foreground-secondary leading-relaxed">
              Experience the future of intelligent conversations with our advanced AI-powered chat platform.
            </p>
          </motion.div>

          {/* Feature List */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="space-y-4"
          >
            {[
              { icon: <BrainIcon className="h-5 w-5" />, text: "Advanced AI Models", desc: "GPT-4, Claude, and more" },
              { icon: <ZapIcon className="h-5 w-5" />, text: "Lightning Fast", desc: "Instant responses" },
              { icon: <SparklesIcon className="h-5 w-5" />, text: "Smart Analysis", desc: "Deep understanding" },
            ].map((feature, index) => (
              <motion.div
                key={feature.text}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                className="flex items-center gap-4 p-3 rounded-lg bg-background-secondary/30 backdrop-blur-sm border border-border/20"
              >
                <div className="p-2 rounded-lg bg-primary/10 text-primary">
                  {feature.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{feature.text}</h3>
                  <p className="text-sm text-foreground-muted">{feature.desc}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-md w-full space-y-8 p-8 bg-background-secondary/20 backdrop-blur-xl border border-border/30 rounded-2xl shadow-2xl relative"
        >
          {/* Card Background Effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-white/0 rounded-2xl" />
          
          <div className="relative z-10">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-center mb-8"
            >
              <h1 className="text-3xl font-bold text-foreground mb-2">
                Welcome back
              </h1>
              
              {/* Continuously Reloading Text Animation */}
              <div className="h-14 flex items-center justify-center mb-4">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentTextIndex}
                    initial={{ opacity: 0, y: 20, scale: 0.8 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.8 }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                    className={`flex items-center gap-3 px-4 py-2 rounded-full bg-gradient-to-r ${rotatingTexts[currentTextIndex].gradient} text-white shadow-lg text-sm`}
                  >
                    {rotatingTexts[currentTextIndex].icon}
                    <span className="font-semibold">
                      {rotatingTexts[currentTextIndex].text}
                    </span>
                  </motion.div>
                </AnimatePresence>
              </div>
              
              <p className="text-foreground-secondary">
                Sign in to your account to continue
              </p>
            </motion.div>

            {/* Form */}
            <motion.form
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              onSubmit={handleSubmit}
              className="space-y-6"
            >
              {/* Email Field */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.5 }}
              >
                <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
                  Email address
                </label>
                <div className="relative">
                  <motion.div
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 z-10"
                    animate={{
                      color: focusedField === 'email' ? '#FF6B6B' : '#6B7280'
                    }}
                  >
                    <MailIcon className="h-5 w-5" />
                  </motion.div>
                  <motion.div
                    whileFocus={{ scale: 1.02 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      onFocus={() => setFocusedField('email')}
                      onBlur={() => setFocusedField(null)}
                      required
                      className="pl-12 bg-input/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-primary/25 transition-all duration-200 rounded-xl"
                      placeholder="Enter your email"
                    />
                  </motion.div>
                  {/* Focus indicator */}
                  <AnimatePresence>
                    {focusedField === 'email' && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="absolute inset-0 border-2 border-primary/30 rounded-xl pointer-events-none"
                      />
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>

              {/* Password Field */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.6 }}
              >
                <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                  Password
                </label>
                <div className="relative">
                  <motion.div
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 z-10"
                    animate={{
                      color: focusedField === 'password' ? '#FF6B6B' : '#6B7280'
                    }}
                  >
                    <LockIcon className="h-5 w-5" />
                  </motion.div>
                  <motion.div
                    whileFocus={{ scale: 1.02 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onFocus={() => setFocusedField('password')}
                      onBlur={() => setFocusedField(null)}
                      required
                      className="pl-12 pr-12 bg-input/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-primary/25 transition-all duration-200 rounded-xl"
                      placeholder="Enter your password"
                    />
                  </motion.div>
                  <motion.button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 z-10 text-foreground-muted hover:text-foreground transition-colors"
                  >
                    {showPassword ? (
                      <EyeOffIcon className="h-5 w-5" />
                    ) : (
                      <EyeIcon className="h-5 w-5" />
                    )}
                  </motion.button>
                  {/* Focus indicator */}
                  <AnimatePresence>
                    {focusedField === 'password' && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="absolute inset-0 border-2 border-primary/30 rounded-xl pointer-events-none"
                      />
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>

              {/* Remember Me & Forgot Password */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 }}
                className="flex items-center justify-between"
              >
                <div className="flex items-center">
                  <motion.input
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-primary focus:ring-primary border-border rounded transition-all duration-200"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-foreground-secondary">
                    Remember me
                  </label>
                </div>
                <div className="text-sm">
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Link href="/auth/forgot-password" className="font-medium text-primary hover:text-primary/80 transition-colors duration-200">
                      Forgot password?
                    </Link>
                  </motion.div>
                </div>
              </motion.div>

              {/* Sign In Button */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.8 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary shadow-lg hover:shadow-primary/25 transition-all duration-300 relative overflow-hidden rounded-xl h-12 group"
                  disabled={isLoading}
                >
                  {isLoading && (
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                      animate={{ x: ['-100%', '100%'] }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                  )}
                  <div className="flex items-center justify-center gap-2 relative z-10">
                    <span className="font-semibold">
                      {isLoading ? 'Signing in...' : 'Sign in'}
                    </span>
                    {!isLoading && (
                      <motion.div
                        animate={{ x: [0, 4, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                      >
                        <ArrowRightIcon className="h-4 w-4" />
                      </motion.div>
                    )}
                  </div>
                </Button>
              </motion.div>

              {/* Sign Up Link */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.9 }}
                className="text-center pt-4"
              >
                <p className="text-sm text-foreground-secondary">
                  Don&apos;t have an account?{' '}
                  <motion.span whileHover={{ scale: 1.05 }} className="inline-block">
                    <Link href="/auth/signup" className="font-medium text-primary hover:text-primary/80 transition-colors duration-200">
                      Sign up
                    </Link>
                  </motion.span>
                </p>
              </motion.div>
            </motion.form>
          </div>
        </motion.div>
      </div>
    </div>
  )
}