'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { BrainIcon, SparklesIcon, ZapIcon, HardDriveIcon } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentTextIndex, setCurrentTextIndex] = useState(0)
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background-secondary to-background relative overflow-hidden">
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
      </div>

      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="max-w-md w-full space-y-8 p-8 relative z-10"
      >
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-center"
        >
          <motion.h1
            className="text-4xl font-bold text-foreground mb-4 bg-gradient-to-r from-foreground to-foreground-secondary bg-clip-text text-transparent"
            animate={{ 
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
            }}
            transition={{ 
              duration: 3, 
              repeat: Infinity, 
              ease: "easeInOut" 
            }}
          >
            Welcome back
          </motion.h1>
          
          {/* Continuously Reloading Text Animation */}
          <div className="h-16 flex items-center justify-center mb-4">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentTextIndex}
                initial={{ opacity: 0, y: 20, scale: 0.8 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.8 }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                className={`flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-to-r ${rotatingTexts[currentTextIndex].gradient} text-white shadow-lg`}
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, ease: "linear" }}
                >
                  {rotatingTexts[currentTextIndex].icon}
                </motion.div>
                <span className="font-semibold text-lg">
                  {rotatingTexts[currentTextIndex].text}
                </span>
              </motion.div>
            </AnimatePresence>
          </div>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-foreground-secondary"
          >
            Sign in to your account to continue
          </motion.p>
        </motion.div>

        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
              Email address
            </label>
            <motion.div whileFocus={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-input/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-primary/25 transition-all duration-200"
                placeholder="Enter your email"
              />
            </motion.div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
              Password
            </label>
            <motion.div whileFocus={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-input/50 backdrop-blur-sm border-border/50 focus:border-primary/50 focus:ring-primary/25 transition-all duration-200"
                placeholder="Enter your password"
              />
            </motion.div>
          </motion.div>

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
                  Forgot your password?
                </Link>
              </motion.div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary shadow-lg hover:shadow-primary/25 transition-all duration-300 relative overflow-hidden"
              disabled={isLoading}
            >
              {isLoading && (
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
              )}
              <span className="relative z-10">
                {isLoading ? 'Signing in...' : 'Sign in'}
              </span>
            </Button>
          </motion.div>
        </motion.form>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.9 }}
          className="text-center"
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
      </motion.div>
    </div>
  )
}