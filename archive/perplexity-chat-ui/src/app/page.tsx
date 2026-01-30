'use client'

import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { SparklesIcon, MessageSquareIcon, MicIcon, FileIcon, BrainIcon, ZapIcon, GlobeIcon, HardDriveIcon, CombineIcon, ArrowRightIcon, PlayIcon, ChevronDownIcon } from 'lucide-react'
import ClientOnly from '@/components/ui/client-only'
import { motion, AnimatePresence } from 'framer-motion'

export default function Home() {
  const router = useRouter()
  const [currentFeature, setCurrentFeature] = useState(0)

  const features = [
    { 
      title: "AI-Powered Search", 
      description: "Get instant answers from multiple sources", 
      icon: <BrainIcon className="h-6 w-6" />,
      gradient: "from-blue-500 to-purple-600"
    },
    { 
      title: "Document Analysis", 
      description: "Upload and analyze any file format", 
      icon: <FileIcon className="h-6 w-6" />,
      gradient: "from-green-500 to-teal-600"
    },
    { 
      title: "Voice Interactions", 
      description: "Natural voice conversations", 
      icon: <MicIcon className="h-6 w-6" />,
      gradient: "from-orange-500 to-pink-600"
    },
    { 
      title: "Lightning Fast", 
      description: "Instant responses powered by AI", 
      icon: <ZapIcon className="h-6 w-6" />,
      gradient: "from-yellow-500 to-red-600"  
    }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background-secondary to-background relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary/20 to-primary-hover/20 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 20,
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
            duration: 18,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Floating Elements */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-primary/30 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              scale: [1, 2, 1],
              opacity: [0.3, 0.8, 0.3],
              y: [0, -20, 0],
            }}
            transition={{
              duration: 4 + Math.random() * 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: Math.random() * 2
            }}
          />
        ))}
      </div>

      <div className="relative z-10">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="min-h-screen flex items-center justify-center px-4"
        >
          <div className="max-w-6xl w-full text-center">
            {/* Main Hero */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mb-16"
            >
              <div className="flex items-center justify-center gap-4 mb-6">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-primary/20 to-primary-hover/20 backdrop-blur-sm">
                  <SparklesIcon className="h-12 w-12 text-primary" />
                </div>
                <h1 className="text-6xl md:text-7xl font-bold text-white">
                  AI Chat
                </h1>
              </div>
              
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="text-2xl md:text-3xl text-white/80 max-w-4xl mx-auto mb-4 leading-relaxed"
              >
                Your intelligent companion for conversations, research, and productivity
              </motion.p>

              {/* Rotating Feature Display */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="h-20 flex items-center justify-center mb-12"
              >
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentFeature}
                    initial={{ opacity: 0, y: 20, scale: 0.8 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.8 }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                    className={`flex items-center gap-4 px-8 py-4 rounded-2xl bg-gradient-to-r ${features[currentFeature].gradient} text-white shadow-2xl`}
                  >
                    <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                      {features[currentFeature].icon}
                    </div>
                    <div className="text-left">
                      <h3 className="text-xl font-bold">{features[currentFeature].title}</h3>
                      <p className="text-white/90">{features[currentFeature].description}</p>
                    </div>
                  </motion.div>
                </AnimatePresence>
              </motion.div>

              {/* CTA Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                className="flex flex-col sm:flex-row gap-6 justify-center"
              >
                <motion.div
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    size="lg"
                    onClick={() => router.push('/chat')}
                    className="text-xl px-12 py-6 bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary shadow-2xl hover:shadow-primary/25 transition-all duration-300 relative overflow-hidden group"
                  >
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                      animate={{ x: ['-100%', '100%'] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    />
                    <div className="flex items-center gap-3 relative z-10">
                      <MessageSquareIcon className="h-6 w-6" />
                      <span>Start Chatting</span>
                      <motion.div
                        animate={{ x: [0, 4, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                      >
                        <ArrowRightIcon className="h-5 w-5" />
                      </motion.div>
                    </div>
                  </Button>
                </motion.div>

                <motion.div
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => router.push('/auth/login')}
                    className="text-xl px-12 py-6 border-2 border-border/50 hover:border-primary/50 bg-background/50 backdrop-blur-sm hover:bg-primary/5 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-3">
                      <PlayIcon className="h-6 w-6 group-hover:text-primary transition-colors" />
                      <span>Watch Demo</span>
                    </div>
                  </Button>
                </motion.div>
              </motion.div>
            </motion.div>

            {/* Scroll Indicator */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.2 }}
              className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
            >
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="flex flex-col items-center gap-2 text-white/60"
              >
                <span className="text-sm">Scroll to explore</span>
                <ChevronDownIcon className="h-5 w-5" />
              </motion.div>
            </motion.div>
          </div>
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="py-24 px-4"
        >
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Powerful Features
              </h2>
              <p className="text-xl text-white/70 max-w-3xl mx-auto">
                Everything you need for intelligent conversations and productivity
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: <MessageSquareIcon className="h-8 w-8" />,
                  title: "Smart Conversations",
                  description: "Engage with GPT-4, Claude, and Gemini models for natural, intelligent dialogue",
                  gradient: "from-blue-500 to-purple-600"
                },
                {
                  icon: <FileIcon className="h-8 w-8" />,
                  title: "Document Analysis",
                  description: "Upload and analyze PDFs, images, and documents with AI-powered insights",
                  gradient: "from-green-500 to-teal-600"
                },
                {
                  icon: <MicIcon className="h-8 w-8" />,
                  title: "Voice Interactions",
                  description: "Speak naturally with voice messages and audio recordings",
                  gradient: "from-orange-500 to-pink-600"
                }
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -10, scale: 1.02 }}
                  className="bg-background-secondary/50 backdrop-blur-sm p-8 rounded-2xl border border-border/50 hover:border-primary/30 transition-all duration-300 relative overflow-hidden group"
                >
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-5`} />
                  </div>
                  <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 text-white shadow-lg relative z-10`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-2xl font-semibold text-white mb-4 relative z-10">
                    {feature.title}
                  </h3>
                  <p className="text-white/70 leading-relaxed relative z-10">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Search Modes Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="py-24 px-4 bg-gradient-to-r from-background-secondary/30 to-background/30 backdrop-blur-sm"
        >
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Flexible Search Modes
              </h2>
              <p className="text-xl text-white/70 max-w-3xl mx-auto">
                Choose how you want to access information
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: <GlobeIcon className="h-8 w-8" />,
                  title: "Online Search",
                  description: "Access real-time information from across the web",
                  gradient: "from-blue-400 to-cyan-500"
                },
                {
                  icon: <HardDriveIcon className="h-8 w-8" />,
                  title: "Local Knowledge",
                  description: "Search through your personal documents and data",
                  gradient: "from-green-400 to-emerald-500"
                },
                {
                  icon: <CombineIcon className="h-8 w-8" />,
                  title: "Combined Search",
                  description: "Best of both worlds for comprehensive results",
                  gradient: "from-purple-400 to-pink-500"
                }
              ].map((mode, index) => (
                <motion.div
                  key={mode.title}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ scale: 1.05, rotateY: 5 }}
                  className="text-center p-8 rounded-2xl bg-background/50 backdrop-blur-sm border border-border/50 hover:border-primary/30 transition-all duration-300"
                >
                  <div className={`w-20 h-20 bg-gradient-to-br ${mode.gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 text-white shadow-2xl`}>
                    {mode.icon}
                  </div>
                  <h3 className="text-2xl font-semibold text-white mb-4">
                    {mode.title}
                  </h3>
                  <p className="text-white/70 leading-relaxed">
                    {mode.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="py-24 px-4"
        >
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="mb-12"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Ready to get started?
              </h2>
              <p className="text-xl text-white/70 mb-8">
                Join thousands of users already using AI Chat for smarter conversations
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="flex flex-col sm:flex-row gap-6 justify-center"
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  size="lg"
                  onClick={() => router.push('/chat')}
                  className="text-xl px-12 py-6 bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary shadow-2xl hover:shadow-primary/25 transition-all duration-300"
                >
                  <div className="flex items-center gap-3">
                    <MessageSquareIcon className="h-6 w-6" />
                    <span>Start for Free</span>
                  </div>
                </Button>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => router.push('/auth/login')}
                  className="text-xl px-12 py-6 border-2 border-border/50 hover:border-primary/50 bg-background/50 backdrop-blur-sm hover:bg-primary/5 transition-all duration-300"
                >
                  Sign In
                </Button>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
