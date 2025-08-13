from fastapi import FastAPI
from router.privacytelemetryapi import router as api_router
from router.moderationtelemetryapi import moderationRouter 
from router.coupledmoderationtelemetryapi import coupledModerationRouter
from router.admintelemetryapi import adminRouter
from router.accMastertelemetryApi import accMasterRouter
from router.authenticatetelemetryApi import authenticateRouter
'''
MIT license https://opensource.org/licenses/MIT
Copyright 2024 Infosys Ltd
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from router.registertelemetryApi import registerRouter
from router.profanitytelemetryapi import profanityRouter
from router.explainabilitytelemetryapi import explainabilityRouter
from router.errorlogtelemetryapi import errorlogRouter
from router.errorloggingtelemetryapi import errorloggingRouter
from router.evalLLMtelemetryapi import evalLLM
from config.config import read_config_yaml
app = FastAPI(**read_config_yaml('./config/metadata.yml'))
app.include_router(api_router, prefix='/rai/v1/telemetry', tags=["Privacy_Telemetry"])
app.include_router(moderationRouter, prefix='/rai/v1/telemetry', tags=["Moderation_Telemetry"])
app.include_router(coupledModerationRouter, prefix='/rai/v1/telemetry', tags=["Coupled Moderation_Telemetry"])
app.include_router(adminRouter, prefix='/rai/v1/telemetry', tags=["Admin_Telemetry"])
app.include_router(errorloggingRouter, prefix='/rai/v1/telemetry', tags=["Error Log_All_TENETS_Telemetry"])
app.include_router(accMasterRouter, prefix='/rai/v1/telemetry', tags=["Account Master_Telemetry"])
app.include_router(authenticateRouter, prefix='/rai/v1/telemetry', tags=["Authentication_Telemetry"])
app.include_router(registerRouter, prefix='/rai/v1/telemetry', tags=["Registration_Telemetry"])
app.include_router(profanityRouter, prefix='/rai/v1/telemetry', tags=["Profanity_Telemetry"])
app.include_router(explainabilityRouter, prefix='/rai/v1/telemetry', tags=["Explainability_Telemetry"])
app.include_router(errorlogRouter, prefix='/rai/v1/telemetry', tags=["Error Log_OLD_Telemetry"])
app.include_router(evalLLM, prefix='/rai/v1/telemetry', tags=["Eval LLM_Telemetry"])
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)