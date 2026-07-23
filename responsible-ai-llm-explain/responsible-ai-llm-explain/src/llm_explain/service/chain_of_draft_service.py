from llm_explain.mappers.mappers import ChainOfDraftRequest, ChainOfDraftResponse        
from llm_explain.service.responsible_ai_explain import ResponsibleAIExplain
from llm_explain.config.logger import CustomLogger

log = CustomLogger()

async def chain_of_draft(payload: ChainOfDraftRequest) -> ChainOfDraftResponse:
    """
    Generate structured reasoning using Chain of Draft technique.
    Args: paylood: Request containing query and optional reasoning text.
    Returns: ChainOfDraftResponse: Response with reasoning steps.
    """
    try:
        log.debug(f"Chain of Draft payload: {payload}")
        
        query = payload.inputPrompt
        reasoning_text = payload.reasoningText
        modelName = payload.modelName
        maxSteps = payload.maxSteps if payload.maxSteps else 10
        endpointDetails = payload.endpointDetails
        
        # Extract endpoint details if provided
        if endpointDetails is not None and ((endpointDetails.modelEndpointUrl is not None and endpointDetails.modelEndpointUrl != "") and 
                                            (endpointDetails.endpointInputParam is not None and endpointDetails.endpointInputParam != "") and 
                                            (endpointDetails.endpointOutputParam is not None and endpointDetails.endpointOutputParam != "")):
            modelEndpointUrl = endpointDetails.modelEndpointUrl
            endpointInputParam = endpointDetails.endpointInputParam
            endpointOutputParam = endpointDetails.endpointOutputParam
        else:
            modelEndpointUrl = None
            endpointInputParam = None
            endpointOutputParam = None
        
        # Call the Chain of Draft method
        response = await ResponsibleAIExplain.chain_of_draft(
            query=query,
            reasoning_text=reasoning_text,
            modelName=modelName,
            maxSteps=maxSteps,
            modelEndpointUrl=modelEndpointUrl,
            endpointInputParam=endpointInputParam,
            endpointOutputParam=endpointOutputParam
        )
        
        log.debug(f"Chain of Draft response: {response}")
        
        return ChainOfDraftResponse(
            query=response.get('query'),
            steps=response.get('steps', []),
            step_count=response.get('step_count', 0),
            consistency_metadata=response.get('consistency_metadata', {}),
            summary=response.get('summary', ''),
            time_taken=response.get('time_taken', 0),
            token_cost=response.get('token_cost')
        )
    except ValueError as e:
        log.error(e, exc_info=True)
        raise
    except Exception as e:
        log.error(e, exc_info=True)
        raise
