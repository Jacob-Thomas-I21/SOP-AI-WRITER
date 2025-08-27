import React, { useState, useCallback, useEffect } from 'react';
import { PharmaceuticalDepartment, SOPPriority, RegulatoryFramework } from '@/types';
import BasicInfoStep from './wizard-steps/BasicInfoStep';
import RegulatoryFrameworkStep from './wizard-steps/RegulatoryFrameworkStep';
import ContentDetailsStep from './wizard-steps/ContentDetailsStep';
import ReviewAndGenerationStep from './wizard-steps/ReviewAndGenerationStep';
import apiService from '../../services/api';

interface WizardStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<any>;
}

interface SOPCreationData {
  // Basic Info
  title: string;
  description: string;
  department: PharmaceuticalDepartment;
  priority: SOPPriority;
  
  // Regulatory Framework
  frameworks: RegulatoryFramework[];
  customRequirements: string;
  complianceNotes: string;
  
  // Content Details
  sections: Array<{
    title: string;
    content: string;
    order: number;
  }>;
  estimatedDuration: string;
  equipmentRequired: string[];
  materialsRequired: string[];
  safetyConsiderations: string;
  qualityCheckpoints: string[];
}

const SOPCreationWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generatedSOP, setGeneratedSOP] = useState<any>(null); // Used in handleGenerate
  // Removed unused isAuthInitialized state
  
  const [wizardData, setWizardData] = useState<SOPCreationData>({
    title: '',
    description: '',
    department: PharmaceuticalDepartment.PRODUCTION,
    priority: SOPPriority.MEDIUM,
    frameworks: [RegulatoryFramework.FDA_21_CFR_211], // Default mandatory framework
    customRequirements: '',
    complianceNotes: '',
    sections: [
      { title: 'Purpose', content: '', order: 1 },
      { title: 'Scope', content: '', order: 2 },
      { title: 'Responsibilities', content: '', order: 3 },
      { title: 'Procedure', content: '', order: 4 },
      { title: 'Documentation', content: '', order: 5 }
    ],
    estimatedDuration: '',
    equipmentRequired: [],
    materialsRequired: [],
    safetyConsiderations: '',
    qualityCheckpoints: []
  });

  const steps: WizardStep[] = [
    {
      id: 'basic-info',
      title: 'Basic Information',
      description: 'SOP title, description, department, and priority',
      component: BasicInfoStep
    },
    {
      id: 'regulatory-framework',
      title: 'Regulatory Framework',
      description: 'Applicable regulations and compliance requirements',
      component: RegulatoryFrameworkStep
    },
    {
      id: 'content-details',
      title: 'Content Details',
      description: 'Sections, equipment, safety, and quality requirements',
      component: ContentDetailsStep
    },
    {
      id: 'review-generation',
      title: 'Review & Generation',
      description: 'Review configuration and generate SOP document',
      component: ReviewAndGenerationStep
    }
  ];

  const updateWizardData = useCallback((stepData: Partial<SOPCreationData>) => {
    setWizardData(prev => ({
      ...prev,
      ...stepData
    }));
  }, []);

  const validateStep = (stepIndex: number): boolean => {
    switch (stepIndex) {
      case 0: // Basic Info
        return !!(wizardData.title && wizardData.description && wizardData.department && wizardData.priority);
      
      case 1: // Regulatory Framework
        return wizardData.frameworks.length > 0;
      
      case 2: // Content Details
        return wizardData.sections.length > 0 && wizardData.sections.every(s => s.title.trim().length > 0);
      
      case 3: // Review & Generation
        return true; // Always valid as it's the final step
      
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1 && validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  // Initialize demo authentication on component mount
  useEffect(() => {
    const initializeDemo = async () => {
      const initialized = await apiService.initializeDemo();
      if (!initialized) {
        console.warn('Demo authentication not initialized - some features may not work');
      }
    };
    initializeDemo();
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerationProgress(0);

    try {
      // Simulate generation progress
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 10;
        });
      }, 500);

      // Prepare API request data
      const requestData = {
        job_id: `sop_${Date.now()}`,
        created_by: "demo_user",
        title: wizardData.title,
        description: wizardData.description,
        template_type: "pharmaceutical_standard",
        department: wizardData.department,
        priority: wizardData.priority,
        regulatory_framework: wizardData.frameworks,
        guideline_refs: wizardData.customRequirements ? [wizardData.customRequirements] : [],
        regulatory_version: "1.0",
        template_content: JSON.stringify({
          sections: wizardData.sections.map(section => ({
            title: section.title,
            content: section.content || `Detailed content for ${section.title} section will be generated based on pharmaceutical best practices and regulatory requirements.`,
            order: section.order
          })),
          equipment_required: wizardData.equipmentRequired.filter(eq => eq.trim()),
          materials_required: wizardData.materialsRequired.filter(mat => mat.trim()),
          safety_considerations: wizardData.safetyConsiderations || 'Safety considerations will be generated based on pharmaceutical operations and regulatory requirements.',
          quality_checkpoints: wizardData.qualityCheckpoints.filter(qc => qc.trim()),
          estimated_duration: wizardData.estimatedDuration,
          custom_requirements: wizardData.customRequirements,
          compliance_notes: wizardData.complianceNotes
        }),
        guideline_content: wizardData.customRequirements || ""
      };

      // Use API service
      const result = await apiService.createSOP(requestData);
      
      clearInterval(progressInterval);
      setGeneratedSOP(result);
      setGenerationProgress(100);
      
      // Show success for a moment, then redirect or show download options
      setTimeout(() => {
        // Handle successful generation - could navigate to result page
        console.log('SOP generated successfully:', result);
      }, 1000);
      
    } catch (error) {
      console.error('SOP generation failed:', error);
      setGenerationProgress(0);
      // Handle error - show error message to user
    } finally {
      setIsGenerating(false);
    }
  };

  const getCurrentStepComponent = () => {
    const StepComponent = steps[currentStep].component;
    
    const commonProps = {
      data: wizardData,
      onUpdate: updateWizardData,
      canProceed: validateStep(currentStep)
    };

    switch (currentStep) {
      case 0:
        return (
          <StepComponent
            {...commonProps}
            onNext={handleNext}
          />
        );
      
      case 1:
        return (
          <StepComponent
            {...commonProps}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      
      case 2:
        return (
          <StepComponent
            {...commonProps}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      
      case 3:
        return (
          <StepComponent
            {...commonProps}
            onBack={handleBack}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            generationProgress={generationProgress}
            canGenerate={validateStep(0) && validateStep(1) && validateStep(2)}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            SOP Creation Wizard
          </h1>
          <p className="text-lg text-gray-600">
            Create pharmaceutical SOPs with AI assistance and regulatory compliance
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                    index < currentStep
                      ? 'bg-green-500 border-green-500 text-white'
                      : index === currentStep
                      ? 'bg-blue-500 border-blue-500 text-white'
                      : 'bg-white border-gray-300 text-gray-500'
                  }`}
                >
                  {index < currentStep ? (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </div>
                
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-4 ${
                      index < currentStep ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          
          <div className="flex justify-between mt-2">
            {steps.map((step, index) => (
              <div key={step.id} className="flex-1 text-center">
                <div className={`text-sm font-medium ${
                  index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                }`}>
                  {step.title}
                </div>
                <div className={`text-xs ${
                  index <= currentStep ? 'text-gray-600' : 'text-gray-400'
                }`}>
                  {step.description}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          {getCurrentStepComponent()}
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>
            Step {currentStep + 1} of {steps.length} • 
            Pharmaceutical SOP Author with AI-powered generation
          </p>
        </div>
      </div>
    </div>
  );
};

export default SOPCreationWizard;