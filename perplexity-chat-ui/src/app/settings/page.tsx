'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useChatStore } from '@/store/chat-store'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  ArrowLeftIcon, 
  UserIcon, 
  BrainIcon, 
  PaletteIcon, 
  VolumeXIcon,
  BellIcon,
  ShieldIcon,
  DatabaseIcon,
  MonitorIcon,
  MoonIcon,
  SunIcon,
  SettingsIcon
} from 'lucide-react'

export default function SettingsPage() {
  const { settings, updateSettings } = useChatStore()
  const [theme, setTheme] = useState('dark')
  const [notifications, setNotifications] = useState(true)
  const [soundEnabled, setSoundEnabled] = useState(true)

  const settingsSections = [
    {
      title: 'General',
      icon: <SettingsIcon className="h-5 w-5" />,
      items: [
        { label: 'Theme', value: theme, type: 'toggle' },
        { label: 'Language', value: 'English', type: 'select' },
        { label: 'Auto-save chats', value: true, type: 'toggle' },
      ]
    },
    {
      title: 'AI & Agents',
      icon: <BrainIcon className="h-5 w-5" />,
      items: [
        { label: 'Default Agent', value: settings.agent, type: 'select' },
        { label: 'Detailed Breakdown', value: settings.detailed_breakdown, type: 'toggle' },
        { label: 'Temperature', value: settings.temperature, type: 'slider' },
      ]
    },
    {
      title: 'Notifications',
      icon: <BellIcon className="h-5 w-5" />,
      items: [
        { label: 'Push Notifications', value: notifications, type: 'toggle' },
        { label: 'Sound Effects', value: soundEnabled, type: 'toggle' },
        { label: 'Email Updates', value: false, type: 'toggle' },
      ]
    },
    {
      title: 'Privacy & Security',
      icon: <ShieldIcon className="h-5 w-5" />,
      items: [
        { label: 'Data Collection', value: 'Minimal', type: 'select' },
        { label: 'Chat History', value: 'Local Only', type: 'select' },
        { label: 'Analytics', value: false, type: 'toggle' },
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background-secondary to-background">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary/10 to-primary-hover/10 rounded-full blur-3xl"
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
      </div>

      <div className="relative z-10 max-w-4xl mx-auto p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-4 mb-8"
        >
          <Link href="/chat">
            <motion.button
              whileHover={{ scale: 1.05, x: -2 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 rounded-lg bg-background-secondary/80 border border-border/50 hover:bg-accent transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5 text-foreground" />
            </motion.button>
          </Link>
          
          <div>
            <h1 className="text-3xl font-bold text-foreground bg-gradient-to-r from-foreground to-foreground-secondary bg-clip-text text-transparent">
              Settings
            </h1>
            <p className="text-foreground-secondary mt-1">
              Customize your AI chat experience
            </p>
          </div>
        </motion.div>

        {/* Settings Sections */}
        <div className="grid gap-6">
          {settingsSections.map((section, sectionIndex) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: sectionIndex * 0.1 }}
              className="bg-background-secondary/50 backdrop-blur-sm border border-border/50 rounded-xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  className="p-2 rounded-lg bg-primary/10"
                >
                  {section.icon}
                </motion.div>
                <h2 className="text-xl font-semibold text-foreground">
                  {section.title}
                </h2>
              </div>

              <div className="space-y-4">
                {section.items.map((item, itemIndex) => (
                  <motion.div
                    key={item.label}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: (sectionIndex * 0.1) + (itemIndex * 0.05) }}
                    className="flex items-center justify-between p-3 rounded-lg bg-background/30 border border-border/30 hover:bg-background/50 transition-colors"
                  >
                    <div>
                      <h3 className="font-medium text-foreground">{item.label}</h3>
                      <p className="text-sm text-foreground-secondary">
                        {typeof item.value === 'boolean' 
                          ? (item.value ? 'Enabled' : 'Disabled')
                          : item.value
                        }
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      {item.type === 'toggle' && (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => {
                            if (item.label === 'Push Notifications') {
                              setNotifications(!notifications)
                            } else if (item.label === 'Sound Effects') {
                              setSoundEnabled(!soundEnabled)
                            } else if (item.label === 'Detailed Breakdown') {
                              updateSettings({ detailed_breakdown: !settings.detailed_breakdown })
                            }
                          }}
                          className={`w-12 h-6 rounded-full transition-colors ${
                            item.value 
                              ? 'bg-primary' 
                              : 'bg-border'
                          }`}
                        >
                          <motion.div
                            animate={{ x: item.value ? 24 : 0 }}
                            transition={{ duration: 0.2 }}
                            className="w-6 h-6 bg-white rounded-full shadow-md"
                          />
                        </motion.button>
                      )}

                      {item.type === 'select' && (
                        <Button variant="outline" size="sm">
                          Change
                        </Button>
                      )}

                      {item.type === 'slider' && (
                        <div className="w-24">
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={typeof item.value === 'number' ? item.value : 0}
                            onChange={(e) => updateSettings({ temperature: parseFloat(e.target.value) })}
                            className="w-full h-2 bg-border rounded-lg appearance-none cursor-pointer"
                          />
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="flex gap-4 mt-8"
        >
          <Button
            variant="outline"
            className="flex-1 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/50 transition-colors"
          >
            Reset to Defaults
          </Button>
          <Button
            className="flex-1 bg-gradient-to-r from-primary to-primary-hover hover:from-primary-hover hover:to-primary shadow-lg hover:shadow-primary/25 transition-all duration-200"
          >
            Save Changes
          </Button>
        </motion.div>
      </div>
    </div>
  )
}