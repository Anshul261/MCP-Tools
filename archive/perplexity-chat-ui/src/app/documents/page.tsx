'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Trash2, Upload, RefreshCw, FileText, Database, AlertCircle, CheckCircle2, Clock, ArrowLeft, MessageSquare, Home, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import Link from 'next/link'
import apiClient from '@/lib/api'

interface DocumentInfo {
  filename: string
  size: number
  converted: boolean
  converted_path: string | null
  extension: string
  valid: boolean
}

interface DocumentStats {
  total_documents: number
  converted_documents: number
  total_size_bytes: number
  knowledge_base_loaded: boolean
  source_directory: string
  converted_directory: string
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [stats, setStats] = useState<DocumentStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const fetchDocuments = useCallback(async () => {
    try {
      const [docsData, statsData] = await Promise.all([
        apiClient.getDocuments(),
        apiClient.getDocumentStats()
      ])
      setDocuments(docsData)
      setStats(statsData)
    } catch (error) {
      console.error('Failed to fetch documents:', error)
      toast.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleFileUpload = async (files: File[]) => {
    if (files.length === 0) return

    setUploading(true)
    try {
      const result = await apiClient.uploadDocuments(files)
      
      const processedCount = result.uploaded_files.filter(f => f.processed).length
      const existedCount = result.uploaded_files.filter(f => f.already_existed).length
      
      let message = `${result.total_uploaded} files uploaded successfully`
      if (processedCount > 0) {
        message += `, ${processedCount} processed and indexed`
      }
      if (existedCount > 0) {
        message += `, ${existedCount} already existed`
      }
      if (result.total_failed > 0) {
        message += `, ${result.total_failed} failed`
      }
      
      toast.success(message)
      fetchDocuments()
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload files')
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = Array.from(e.dataTransfer.files)
    handleFileUpload(files)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    handleFileUpload(files)
  }

  const handleDeleteDocument = async (filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return

    try {
      await apiClient.deleteDocument(filename)
      toast.success('Document deleted successfully')
      fetchDocuments()
    } catch (error) {
      console.error('Delete error:', error)
      toast.error('Failed to delete document')
    }
  }

  const handleProcessDocuments = async () => {
    setProcessing(true)
    try {
      const result = await apiClient.processDocuments()
      toast.success(`${result.converted} documents processed and knowledge base updated`)
      fetchDocuments()
    } catch (error) {
      console.error('Process error:', error)
      toast.error('Failed to process documents')
    } finally {
      setProcessing(false)
    }
  }

  const DocumentSkeleton = () => (
    <div className="space-y-2">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="flex items-center justify-between p-4 rounded-lg border bg-card/50 animate-pulse">
          <div className="flex items-center gap-3 flex-1">
            <div className="h-5 w-5 bg-muted rounded" />
            <div className="flex-1">
              <div className="h-4 bg-muted rounded w-48 mb-2" />
              <div className="h-3 bg-muted rounded w-24" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-6 w-16 bg-muted rounded-full" />
            <div className="h-8 w-8 bg-muted rounded" />
          </div>
        </div>
      ))}
    </div>
  )

  const StatsSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <Card key={i} className="animate-pulse">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="h-4 bg-muted rounded w-24" />
            <div className="h-4 w-4 bg-muted rounded" />
          </CardHeader>
          <CardContent>
            <div className="h-8 bg-muted rounded w-16" />
          </CardContent>
        </Card>
      ))}
    </div>
  )

  if (loading) {
    return (
      <div className="container mx-auto p-6 max-w-6xl space-y-6">
        {/* Navigation Header */}
        <div className="flex items-center gap-4 mb-6">
          <Link href="/chat">
            <Button variant="ghost" size="sm" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Chat
            </Button>
          </Link>
          <div className="h-6 w-px bg-border" />
          <Link href="/">
            <Button variant="ghost" size="sm" className="gap-2">
              <Home className="h-4 w-4" />
              Home
            </Button>
          </Link>
          <Link href="/chat">
            <Button variant="outline" size="sm" className="gap-2">
              <MessageSquare className="h-4 w-4" />
              Chat
            </Button>
          </Link>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Document Management</h1>
            <p className="text-muted-foreground">
              Manage your document knowledge base for AI-powered search and analysis
            </p>
          </div>
        </div>

        {/* Loading Stats */}
        <StatsSkeleton />

        {/* Loading Upload Area */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Documents</CardTitle>
            <CardDescription>
              Drag and drop files here or click to browse. Supported formats: PDF, DOCX, PPTX, TXT
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
              <div className="h-12 w-12 mx-auto mb-4 bg-muted rounded animate-pulse" />
              <div className="h-6 bg-muted rounded w-48 mx-auto mb-2 animate-pulse" />
              <div className="h-4 bg-muted rounded w-32 mx-auto mb-2 animate-pulse" />
              <div className="h-10 bg-muted rounded w-24 mx-auto animate-pulse" />
            </div>
          </CardContent>
        </Card>

        {/* Loading Document List */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Document Library</CardTitle>
              <CardDescription>Loading your document collection...</CardDescription>
            </div>
            <div className="h-10 bg-muted rounded w-32 animate-pulse" />
          </CardHeader>
          <CardContent>
            <DocumentSkeleton />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl space-y-6">
      {/* Navigation Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/chat">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Chat
          </Button>
        </Link>
        <div className="h-6 w-px bg-border" />
        <Link href="/">
          <Button variant="ghost" size="sm" className="gap-2">
            <Home className="h-4 w-4" />
            Home
          </Button>
        </Link>
        <Link href="/chat">
          <Button variant="outline" size="sm" className="gap-2">
            <MessageSquare className="h-4 w-4" />
            Chat
          </Button>
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Document Management</h1>
          <p className="text-muted-foreground">
            Manage your document knowledge base for AI-powered search and analysis
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="transition-all duration-300 hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold transition-all duration-500">
              {stats?.total_documents || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processed</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold transition-all duration-500">
              {stats?.converted_documents || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Size</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold transition-all duration-500">
              {formatFileSize(stats?.total_size_bytes || 0)}
            </div>
          </CardContent>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Knowledge Base</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {stats?.knowledge_base_loaded ? (
                <Badge variant="default" className="bg-green-500 transition-all duration-300">
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    Active
                  </div>
                </Badge>
              ) : (
                <Badge variant="secondary">Empty</Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
          <CardDescription>
            Drag and drop files here or click to browse. Supported formats: PDF, DOCX, PPTX, TXT
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
              uploading
                ? 'border-primary bg-primary/10 scale-[1.02]'
                : dragActive
                ? 'border-primary bg-primary/10 scale-[1.01]'
                : 'border-muted-foreground/25 hover:border-muted-foreground/50 hover:bg-muted/5'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            {uploading ? (
              <div className="space-y-4">
                <div className="relative">
                  <Loader2 className="h-12 w-12 mx-auto text-primary animate-spin" />
                  <div className="absolute inset-0 rounded-full border-2 border-primary/20 animate-pulse" />
                </div>
                <div className="space-y-2">
                  <p className="text-lg font-medium text-primary">Processing Documents...</p>
                  <p className="text-sm text-muted-foreground">Converting and indexing for search</p>
                  <div className="w-48 mx-auto bg-muted rounded-full h-2 overflow-hidden">
                    <div className="bg-primary h-full animate-pulse" />
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div className={`transition-transform duration-200 ${dragActive ? 'scale-110' : ''}`}>
                  <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                </div>
                <div className="space-y-2">
                  <p className="text-lg font-medium">
                    {dragActive ? 'Drop files here' : 'Drag & drop files here'}
                  </p>
                  <p className="text-sm text-muted-foreground">or</p>
                  <label htmlFor="file-upload">
                    <Button variant="outline" disabled={uploading} asChild>
                      <span className="cursor-pointer">
                        'Browse Files'
                      </span>
                    </Button>
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    multiple
                    className="hidden"
                    accept=".pdf,.docx,.pptx,.txt"
                    onChange={handleFileInput}
                    disabled={uploading}
                  />
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Documents List */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Document Library</CardTitle>
            <CardDescription>
              {documents.length} document{documents.length !== 1 ? 's' : ''} in your knowledge base
            </CardDescription>
          </div>
          <Button
            onClick={handleProcessDocuments}
            disabled={processing || documents.length === 0}
            variant="outline"
            className={processing ? 'bg-primary/10 border-primary text-primary' : ''}
          >
            {processing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Database className="h-4 w-4 mr-2" />
                Process All
              </>
            )}
          </Button>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No documents uploaded yet</p>
              <p className="text-sm">Upload some documents to get started</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.filename}
                  className="flex items-center justify-between p-4 rounded-lg border bg-card/50 hover:bg-card/80 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{doc.filename}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>{formatFileSize(doc.size)}</span>
                        <span>•</span>
                        <span>{doc.extension.toUpperCase()}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {doc.converted ? (
                      <Badge variant="default" className="bg-green-500">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Processed
                      </Badge>
                    ) : doc.valid ? (
                      <Badge variant="secondary">
                        <Clock className="h-3 w-3 mr-1" />
                        Pending
                      </Badge>
                    ) : (
                      <Badge variant="destructive">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Invalid
                      </Badge>
                    )}

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteDocument(doc.filename)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}